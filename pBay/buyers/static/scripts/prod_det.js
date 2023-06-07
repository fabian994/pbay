
function imgDisplay(imgs) {
    var expandImg = document.getElementById("expandedImg");
    var imgText = document.getElementById("imgtext");
    expandImg.src = imgs.src;
    imgText.innerHTML = imgs.alt;
    expandImg.parentElement.style.display = "block";
  }

  
  $("#linkdet").click(function(){
    var prodlink = document.getElementById("prodName");
    var s = prodlink.value;
    console.log(s);
    });

