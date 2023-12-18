var sdk = apigClientFactory.newClient({});

function callProfilePostApi(user_id) {
  //Should return an object containing user groups, name, features, and pending invites
  var params = {};
  var body = { userId: user_id };
  var additionalParams = {};
  sdk.profilePost(params, body, additionalParams).then((userInfo) => {
    const userGroups = userInfo.data.groups;
    var ledGroups = [];
    for (let i = 0; i < userGroups.length; i++) {
      if (userGroups[i].groupLeader.userId == user_id) {
        ledGroups.push(userGroups[i].groupId);
      }
    }
    localStorage.setItem("_ledGroups", btoa(JSON.stringify(ledGroups)));
    localStorage.setItem("_userFeatures", btoa(JSON.stringify(userInfo.data.userFeatures)));
    localStorage.setItem("_userGroups", btoa(JSON.stringify(userInfo.data.groups)));
    localStorage.setItem("_userInvites", btoa(JSON.stringify(userInfo.data.pendingInvites)));
    //console.log(JSON.stringify(userInfo.data.groups));
    console.log("Updated");
  });
}

function callMatchesPostApi(user_id) {
  params = {};
  body = { userId: user_id };
  additionalParams = {};
  sdk.matchmakerPost(params, body, additionalParams).then((response) => {
    localStorage.setItem("_matches", btoa(JSON.stringify(response)));
    //console.log(JSON.stringify(response));
    return response;
  });
}

function showPrompt(inviteeId, inviteeName, ledGroups) {
  let groupsString = ledGroups[0];
  for (let i = 1; i < ledGroups.length; i++) {
    groupsString += ", " + ledGroups[i];
  }
  while (true) {
    let invitingGroup = prompt(
      "Enter the group ID you want to invite " + inviteeName + " to. Here are your options: " + groupsString + "."
    );
    //console.log(JSON.stringify(ledGroups));
    if (ledGroups.includes(Number(invitingGroup))) {
      let message = "You have invited " + inviteeName + " to group " + invitingGroup;
      callExtendInvitationPostApi({ invitee: inviteeId, currentGroup: Number(invitingGroup) });
      alert(message);
      return Number(invitingGroup);
    }
    if (invitingGroup == null) {
      let message = "You have cancelled the invitation.";
      alert(message);
      return -1;
    }
    alert("Invalid group ID! Please try again.");
  }
}

function callExtendInvitationPostApi(out_invitation) {
  console.log("Invitation Extended to " + out_invitation.invitee + " for group " + out_invitation.currentGroup + ".");
  params = {};
  body = { o_inv: out_invitation };
  additionalParams = {};
  var response = sdk.extendInvitationPost(params, body, additionalParams);
  // console.log("Response: " + response);
  return response;
  // return "Invitation Extended to " + out_invitation.invitee + " for group " + out_invitation.currentGroup + ".";
}

function showHiddenFeatures(hiddenFeatures) {
  var i, x;
  x = document.getElementsByClassName("hidden_feature");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  for (i = 0; i < hiddenFeatures.length; i++) {
    document.getElementById(hiddenFeatures[i]).style.display = "block";
  }
}

window.addEventListener("load", async function () {
  //EDIT THIS TO GET THE USER'S REPRESENTATIVE VECTOR
  const grid = document.getElementById("grid");

  // Save user_id to local storage
  //var account = { userId: user_id };
  //account = btoa(JSON.stringify(account));
  //localStorage.setItem("_account", account);

  const account = JSON.parse(atob(localStorage.getItem("_account")));
  const user_id = account.userId;

  const features = JSON.parse(atob(localStorage.getItem("_userFeatures")));
  console.log("Features: " + JSON.stringify(features));
  // Get first name
  for (let i = 0; i < features.length; i++) {
    if (Object.keys(features[i]) == "first_name") {
      console.log("FOUND");
      var firstName = Object.values(features[i])[0];
    }
  }
  account.firstName = firstName;
  localStorage.setItem("_account", btoa(JSON.stringify(account)));

  console.log("THIS IS THE USER ID: " + user_id);
  window.setInterval(callProfilePostApi(user_id), 8000);

  // send the message to API
  callMatchesPostApi(user_id);
  var response = JSON.parse(atob(localStorage.getItem("_matches")));
  console.log("Response: " + JSON.stringify(response));
  var compats = JSON.parse(response.data.body);
  console.log("Compats: " + JSON.stringify(compats));
  var ledGroups = JSON.parse(atob(localStorage.getItem("_ledGroups")));
  if (compats && compats.length > 0) {
    var displaySet = new Set();
    for (let i = 0; i < compats.length; i++) {
      console.log("ID: " + compats[i].user_id);
      if (displaySet.has(compats[i].user_id)) {
        continue;
      } else {
        var item = document.createElement("div");
        item.setAttribute("data-user-id", compats[i].user_id);
        item.setAttribute("grid-column", (i % 3) + " / span 1");
        item.setAttribute("grid-row", Math.floor(i / 3) + " / span 1");
        item.setAttribute("class", "grid-item");
        item.innerHTML = compats[i].first_name + " " + compats[i].last_name;

        // Add button to grid-item
        var button = document.createElement("button");
        button.setAttribute("class", "extend-button");
        button.setAttribute(
          "onclick",
          "showPrompt(" +
            compats[i].user_id +
            "," +
            '"' +
            compats[i].first_name +
            " " +
            compats[i].last_name +
            '"' +
            "," +
            JSON.stringify(ledGroups) +
            ")"
        );
        button.innerHTML = "Extend Invitation";

        // Display text in grid-item
        const hiddenFeatures = [];

        for (let j = 0; j < Object.entries(compats[i]).length; j++) {
          key = Object.keys(compats[i])[j];
          value = Object.values(compats[i])[j];
          var feature = document.createElement("div");
          //console.log("Feature: " + key + ": " + value);
          feature.innerHTML += key + ": " + value + "<br>";
          feature.setAttribute("class", "feature");
          feature.setAttribute("id", compats[i].user_id + "feature" + j);
          // Hide features after the first two
          if (j > 1) {
            feature.setAttribute("class", "hidden_feature");
            feature.style.display = "none";
            hiddenFeatures.push(feature.id);
          }
          item.appendChild(feature);
          item.setAttribute("onclick", "showHiddenFeatures(" + JSON.stringify(hiddenFeatures) + ")");

          if (j == Object.entries(compats[i]).length - 1) {
            feature.appendChild(button);
          }
        }

        grid.appendChild(item);
        displaySet.add(compats[i].user_id);
      }
    }
  } else {
    console.log("No matches found.");
  }
});
