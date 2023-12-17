//UNCOMMENT RELEVANT LINES WHEN API IS READY

var sdk = apigClientFactory.newClient({});

function callModifyProfilePostApi(user_id, user_vector) {
  params = {}
  body = { currentUser: user_id, newFeatures: user_vector }
  additionalParams = {}
  return sdk.modifyProfilePost(params, body, additionalParams);
}

window.addEventListener("load", function () {
  const editButton = $("#editButton");
  const maxWidth = 50;
  const maxHeight = 50;

  var account = localStorage.getItem('_account');
  account = atob(account);
  account = JSON.parse(account);

  var features = localStorage.getItem("_userFeatures");
  features = atob(features);
  features = JSON.parse(features);

  const user_id = account.userId;
  console.log("THIS IS THE USER ID: " + user_id);
  features.forEach((feature) => {
    var featureName = Object.keys(feature);
    var featureValue = Object.values(feature);
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
    console.log(callModifyProfilePostApi(user_id, features));
  });
});
