var sdk = apigClientFactory.newClient({});
function callMatchesGetApi(user_id) {
    // params, body, additionalParams
    // console.log(message)
    return sdk.matchMakerGet({"UserId": user_id});
}

window.addEventListener("load", function() {
    //EDIT THIS TO GET THE USER'S REPRESENTATIVE VECTOR
    const grid = document.getElementById("grid");
    const user_id = "1";
    // send the message to API
    var response = callMatchesGetApi(user_id)
    console.log(response);
    var compats = response.data.compatibleUsers;
    if (compats && compats.length > 1) {
        //console.log('received ' + (compats.length - 1) + ' matches');
        var displaySet = new Set();
        for (let i = 1; i < compats.length; i++) {
            if (displaySet.has(compats[i].UserId)) {
                continue;
            } else {
                var item = document.createElement("div");
                item.setAttribute("grid-column", (i-1) % 3 + " / span 1");
                item.setAttribute("grid-row", Math.floor((i-1)/3) + " / span 1");
                item.setAttribute("class", "grid-item");
                // Display text in grid-item
                for (let j = 0; j < compats[i].UserFeatures.length; j++) {
                    item.innerHTML += compats[i].UserFeatures[j] + "<br>";
                }
                grid.appendChild(item);
                displaySet.add(compats[i].UserId);
            }
        }
    } else {
        var item = document.createElement("div");
        item.setAttribute("grid-column", (i-1) % 3 + " / span 1");
        item.setAttribute("grid-row", Math.floor((i-1)/3) + " / span 1");
        item.setAttribute("class", "grid-item");
        item.innerHTML = "Empty";
        grid.appendChild(item);
    }
        })
        .catch((error) => {
            var item = document.createElement("div");
            item.setAttribute("grid-column", (i-1) % 3 + " / span 1");
            item.setAttribute("grid-row", Math.floor((i-1)/3) + " / span 1");
            item.setAttribute("class", "grid-item");
            item.innerHTML = "Empty";
            grid.appendChild(item);
            console.log('an error occurred', error);
        });