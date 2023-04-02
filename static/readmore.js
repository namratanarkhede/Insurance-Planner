/*var a;

function show_hide()
{
    if(a==1)
    {
        document.getElementById("f").style.display="inline";
        return a=0;
    }
    else
    {
        document.getElementById("f").style.display="none";
        return a=1;
    }
}

 
var b;
function show_hide1()
{
    if(b==1)
    {
        document.getElementById("c").style.display="inline";
        return b=0;
    }
    else
    {
        document.getElementById("c").style.display="none";
        return b=1;
    }
}

/*
document.getElementById("1").addEventListener("click",myFunction());

function myFunction(){
    document.getElementById("f").textContent;
}

document.getElementById("2").addEventListener("click",myFunction2());

function myFunction2(){
    document.getElementById("c").textContent;
}
*/


function show_hide() {
    var x = document.getElementById("f");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }




    
  function show_hide1() {
    var x = document.getElementById("c");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }


