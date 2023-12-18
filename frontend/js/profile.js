//UNCOMMENT RELEVANT LINES WHEN API IS READY

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

function callModifyProfilePostApi(user_id, user_vector) {
  params = {};
  body = { currentUser: user_id, newFeatures: user_vector };
  additionalParams = {};
  sdk.modifyProfilePost(params, body, additionalParams).then((response) => {
    callProfilePostApi(user_id);
    return response;
  });
}

window.addEventListener("load", function () {
  const editButton = $("#editButton");
  const maxWidth = 50;
  const maxHeight = 50;
  const unchangeableFeatures = ["user_id"];

  var account = localStorage.getItem("_account");
  account = atob(account);
  account = JSON.parse(account);

  var features = localStorage.getItem("_userFeatures");
  features = atob(features);
  features = JSON.parse(features);

  const user_id = account.userId;
  window.setInterval(callProfilePostApi(user_id), 20000);

  console.log("THIS IS THE USER ID: " + user_id);
  features.forEach((feature) => {
    var featureName = Object.keys(feature);
    var featureValue = Object.values(feature);
    console.log(featureName + ": " + featureValue);
    var featureDiv = document.createElement("div");

    featureDiv.setAttribute("class", "feature");
    featureDiv.innerHTML = featureName + ": " + featureValue;
    var profileDiv = document.getElementsByClassName("profile")[0];
    profileDiv.appendChild(featureDiv);

    if (!unchangeableFeatures.includes(featureName[0])) {
      var editField = document.createElement("input");
      editField.setAttribute("type", "text");
      editField.setAttribute("id", featureName);
      editField.style.display = "block";
      profileDiv.appendChild(editField);

      editField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          featureDiv.innerHTML = featureName + ": " + editField.value;
          for (let i = 0; i < features.length; i++) {
            if (Object.keys(features[i])[0] == featureName[0]) {
              // Need to index into featureName because it's an array with one element
              features[i][featureName] = editField.value;
              console.log("Feature Updated: " + featureName + ": " + features[i][featureName]);
            }
          }
          editField.value = "";
        }
      });
    }
  });
  editButton.click(function () {
    console.log(callModifyProfilePostApi(user_id, features));
  });
});
