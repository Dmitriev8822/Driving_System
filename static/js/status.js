var StatusData = document.getElementsByClassName("colum");
for (var i = 0; i < StatusData.length; i++) {
    if(StatusData[i].id == "red")
    {
        StatusData[i].style.backgroundColor = "#AA0000";
    }
}