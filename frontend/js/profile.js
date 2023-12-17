//UNCOMMENT RELEVANT LINES WHEN API IS READY

var sdk = apigClientFactory.newClient({});

function callProfileGetApi(user_id) {
  // Should return an object containing user groups, name, features, and pending invites
  // const userInfo = sdk.profileGet({ UserId: user_id });
  // return userInfo.data.userFeatures; // Should be an array of features (each one is an object containing a name and a value)
  return [
    { featureName: "Feature 1", featureValue: "Value 1" },
    { featureName: "Feature 2", featureValue: "Value 2" },
  ];
}

function callProfilePostApi(user_id, user_vector) {
  // return sdk.profilePost({ currentUser: user_id, newFeatures: user_vector });
  for (let i = 0; i < user_vector.length; i++) {
    console.log(user_vector[i].featureName + ": " + user_vector[i].featureValue);
  }
  return "Success";
}

window.addEventListener("load", function () {
  const editButton = $("#editButton");
  const maxWidth = 50;
  const maxHeight = 50;

  var account = localStorage.getItem('_account');
  account = atob(account);
  account = JSON.parse(account);

  const user_id = account.userId;
  console.log("THIS IS THE USER ID: " + user_id);
  var features = callProfileGetApi(user_id);
  features.forEach((feature) => {
    var featureName = feature.featureName;
    var featureValue = feature.featureValue;
    console.log(featureName + ": " + featureValue);
    var featureDiv = document.createElement("div");

    var editField = document.createElement("input");
    editField.setAttribute("type", "text");
    editField.setAttribute("id", featureName);
    editField.style.display = "block";

    featureDiv.setAttribute("class", "feature");
    featureDiv.innerHTML = featureName + ": " + featureValue;
    // find the div with class "profile" and append the featureDiv to it as a child
    var profileDiv = document.getElementsByClassName("profile")[0];
    profileDiv.appendChild(featureDiv);
    profileDiv.appendChild(editField);

    editField.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        featureDiv.innerHTML = featureName + ": " + editField.value;
        for (let i = 0; i < features.length; i++) {
          if (features[i].featureName === featureName) {
            features[i].featureValue = editField.value;
            console.log("Feature Updated: " + features[i].featureName + ": " + features[i].featureValue);
          }
        }
        editField.value = "";
      }
    });
  });
  editButton.click(function () {
    console.log(callProfilePostApi(user_id, features));
  });
});
