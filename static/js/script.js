// document.getElementById('chat-form').addEventListener('submit', function (event) {
//     event.preventDefault();
  
//     const chatInput = document.getElementById('chat-input').value;
//     const skill = document.getElementById('skill').value;
//   //   const ottPlatform = document.getElementById('ott_platform').value;
//   //   const genre = document.getElementById('preferred_genre').value;
//     const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  
//     fetch('api/chatbot/', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': csrfToken
//       },
//       body: JSON.stringify({
//         chat_input: chatInput,
//         skill: skill,
//       //   ottPlatform: ottPlatform,
//       //   genre: genre,
//       })
//     })
//       .then(response => response.json())
//       .then(data => {
//         console.log("Done")
//         document.getElementById('response-content').innerText = data.content;
  
//         // Text-to-Speech
//         const utterance = new SpeechSynthesisUtterance(data.content);
//         speechSynthesis.speak(utterance);
//       })
//       .catch(error => console.error('Error:', error, chatInput));
//   });

let isRecording = false;
let recognition;

document.getElementById('hold_to_talk').addEventListener('mouseup', stopRecording);
document.getElementById('hold_to_talk').addEventListener('mousedown', startRecording);
document.getElementById('hold_to_talk').addEventListener('mouseleave', stopRecording);

function updateLanguage() {
    const language = document.getElementById('selectedLanguage').value;
    return language
}

function startRecording() {

    if (!isRecording) {
        language = updateLanguage()
        recognition = new webkitSpeechRecognition() || SpeechRecognition();

        isRecording = true;
        console.log('Recording started');

        // Initialize the SpeechRecognition object
        recognition.continuous = true;
        console.log("----lang->>", language)
        if (language == 'Hindi') {
            recognition.lang = 'hi-IN';
        } else {
            recognition.lang = 'en-US';
        }
        
        console.log(recognition.lang);
        // recognition.lang = 'hi-IN';

        // Event handler for when the recognition service returns a result
        recognition.onresult = function (event) {
            const transcript = event.results[event.results.length - 1][0].transcript;
            document.getElementById('chat-input').value = transcript;

        };
        recognition.start();
    }
}

function stopRecording() {
    if (isRecording) {
        recognition.stop();
        console.log('Recording stopped');
        isRecording = false;
    }
}


  document.getElementById('chat-form').addEventListener('submit', function(event) {
      event.preventDefault();
      handleStream();
  });

  function handleStream() {
      const responseDiv = document.getElementById('response');
      responseDiv.innerHTML = ""; // Clear previous responses

      const chat_input = document.getElementById('chat-input').value;
      const skill = document.getElementById('skill').value;

      fetch('api/chatbot/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              chat_input: chat_input,
              skill: skill
          })
      })
      .then(response => {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          function read() {
              reader.read().then(({ done, value }) => {
                  if (done) {
                      return;
                  }
                  const chunk = decoder.decode(value, { stream: true });
                  const newContent = document.createTextNode(chunk);
                  responseDiv.appendChild(newContent);
                  read();
              });
          }
          read();
      })
      .catch(error => {
          console.error('Error:', error);
      });
  }

