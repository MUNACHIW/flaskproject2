

// Get all the radio buttons
let radios = document.querySelectorAll('input[type="radio"]');

// Add a 'change' event listener to each radio button
radios.forEach(radio => {
    radio.addEventListener('change', function() {
        // When a radio button is selected, uncheck all other radio buttons
        radios.forEach(otherRadio => {
            if(otherRadio !== this) {
                otherRadio.checked = false;
            }
        });
    });
});


// Check for saved 'darkMode' in localStorage
if (localStorage.getItem('darkMode')) {
    document.body.classList.add('dark-mode');
    var elements = document.querySelectorAll('.nav, .post, .posted, .layout, .sec, .access, .circle, .profile-area, #inputprofile, .signinform, .exclamation , .VIEW, .post_box, .intro_box, .intomodal, .postaction, .homemobile');
    elements.forEach(function(el) {
        el.classList.add('dark-mode');
    });
}

document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');

    var elements = document.querySelectorAll('.nav, .post, .posted, .layout, .sec, .access, .circle, .profile-area, #inputprofile, .signinform, .exclamation, .VIEW, .post_box, .intro_box, .intomodal, .postaction, .homemobile');
   
    elements.forEach(function(el) {
        el.classList.toggle('dark-mode');
    });

    // Save the current theme in localStorage.
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', true);
    } else {
        localStorage.removeItem('darkMode');
    }
});

if(localStorage.getItem('darkmode')){
  document.body.classList.add('dark-mode');
  var elements =  document.querySelector
};

const x = document.getElementById("inputprofile")
function toggleInput() {

    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

toggleInput();
function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('image-preview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}

window.onbeforeunload = function() {
    $.ajax({
        type: 'POST',
        url: '/logout',  // specify your server-side logout url
        async: false,
        success: function(logged_in_user) {
            console.log("Session cleared");
        }
    });
};


const cover = document.querySelector(".inputcover");
function coverinput(){
     if (cover.style.display === "none"){
        cover.style.display = "block";
     }else{
        cover.style.display ="none";
     }
}

coverinput()




function previewCover(event){
    const read = new FileReader();
    read.onload = function(){
    const output = document.getElementById('cover-preview');
    output.src = read.result;
    output.style.display = 'block';
    }
    read.readAsDataURL(event.target.files[0]);
}



fetch('/get_users')
    .then(response => response.json())
    .then(users => autocomplete(document.getElementById("searchInput"), users));
 // Replace this with your list of users

 function searchUser() {
    let input = document.getElementById('searchInput').value; // get the input value
    let result = document.getElementById('searchResult'); // get the list element
    if (input.length > 1) { // if the input is not empty
      fetch('/search?input=' + input) // send a GET request to the /search route with the input as a query parameter
      .then(response => response.json()) // parse the response as JSON
      .then(data => {
        result.innerHTML = ''; // clear the previous results
        result.style.display = 'block'; // show the list element
        for (let user of data) { // loop through the user data
          let li = document.createElement('a'); // create a list item for each user
          li.textContent = user.username + ' ' + user.surname + ''; // set the text content to the username and email
        // li.textContent = ( user.username )
          li.href  = '/profile/'+user.username+'';
          li.setAttribute('data-id', user.id); // set a data attribute to the user id
          li.addEventListener('click', selectUser); // add a click event listener to the list item
          result.appendChild(li); // append the list item to the list element
        }
      })
      .catch(error => console.error(error)); // handle any errors
    } else { // if the input is empty
      result.style.display = 'none'; // hide the list element
    }
  }

  // create a function to handle the user selection from the autocomplete suggestions
  function selectUser(event) {
    let li = event.target; // get the list item that was clicked
    let id = li.getAttribute('data-id'); // get the user id from the data attribute
    let input = document.getElementById('searchInput'); // get the input element
    let result = document.getElementById('searchResult'); // get the list element
    input.value = li.textContent; // set the input value to the list item text
    result.style.display = 'none'; // hide the list element
    // do something with the user id, such as redirecting to the user profile page
    // window.location.href = '/user/' + id;
  }
  
  
  document.querySelector('.postaction').addEventListener('submit', function(e) {
    var files = document.querySelector('input[type=file]').files;
    if (files.length === 0) {
        e.preventDefault();
        alert('Please select a file to upload');
    }
});


var videos = document.querySelectorAll('video');

window.addEventListener('scroll', function() {
  videos.forEach(video => {
    var rect = video.getBoundingClientRect();
    if(rect.top >= 0 && rect.bottom <= window.innerHeight) {
      video.play();
    } else {
      video.pause();
    }
  });
});

videos.forEach(video => {
  video.addEventListener('play', function() {
    videos.forEach(v => {
      if(v != this) v.pause();
    });
  });
});








function frmSubmit() {
    document.user_id.submit();
 }

