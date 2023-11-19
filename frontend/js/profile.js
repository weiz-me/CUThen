window.submitUserInput = function() {
    //EDIT THIS TO GET THE USER'S ID
    const userInput = userInputField.val();
    
    //userInputField.val('');
    if ($.trim(userInput) !== '') {
      // send the message to API
      displayProfile.empty();
      callAlbumGetApi(user_vector)
          .then((response) => {
              console.log(response);
              var data = response.data.results;
              if (data && data.length > 1) {
                  console.log('received ' + (data.length - 1) + ' matches');
                  var displaySet = new Set();
                  labels = data[0].labels;
                  var label_text = 'Image with label "';
                  if (labels.length == 1) {
                      label_text += labels[0] + '"';
                  } else {
                      label_text += labels[0] + '" and "' + labels[1] + '"';
                  }
                  displayProfile.append($('<h2>').text(label_text));
                  for (let i = 1; i < data.length; i++) {
                      if (displaySet.has(data[i].url)) {
                          continue;
                      } else {
                          displaySet.add(data[i].url);
                          var profileInfo = $('<h2>')
                          var editButton = $('<button>')

                          //EDIT TO SHOW PROFILE INFO PROPERLY

                          // img.load(function(){
                          //     var ratio = Math.min(maxWidth / $(this).width(), maxHeight / $(this).height());
                          //     console.log(ratio);
                          //     console.log($(this).height());
                          //     $(this).attr('width', $(this).width() * ratio);
                          //     $(this).attr('height', $(this).height() * ratio);
                          // });
                          img.appendTo(displayProfile);
                      }
                  }
              } else {
                  var label_text = 'No image found.';
                  displayProfile.append($('<h2>').text(label_text));
              }
          })
          .catch((error) => {
              console.log('an error occurred', error);
          });
    }
  };