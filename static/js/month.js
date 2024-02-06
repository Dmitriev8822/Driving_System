var today = new Date();
var years = today.getFullYear();
window.number = String(today.getMonth() + 1).padStart(2, '0') - 1;
var firstSelect = -1;
var getTime = true;
var StatusData = document.getElementsByClassName("column");


function ButtonClick(n){
    var num_active = $(n).index(".column") + 1; // Номер элемента
    if(n.id == 'selected'){
        for (var i = 0; i < StatusData.length; i++) {
            if(StatusData[i].id == 'selected')
            {
                StatusData[i].id = 'free';
            }
        }
        firstSelect = num_active;
        document.getElementById('workTime1').innerHTML = n.innerHTML;
        document.getElementById('workTime2').innerHTML = "....";
        document.getElementsByName('workTime1')[0].value = n.innerHTML;
        document.getElementsByName('workTime2')[0].value = "....";
        getTime = true;
        n.id = 'selected';
        return;
    }
    else if(n.id == 'free')
    {
        n.id = 'selected';
        if(firstSelect == -1 && getTime) { // Выбрана ли первая граница
            firstSelect = num_active;
            document.getElementById('workTime1').innerHTML = n.innerHTML;
            document.getElementsByName('workTime1')[0].value = n.innerHTML;

            document.getElementsByName('workTime1')[0].value = n.innerHTML;
               document.getElementsByName('workTime2')[0].value = "....";
        }
        else {
            if((parseInt(num_active / 26) - parseInt(firstSelect / 26) != 0) || !getTime || num_active - firstSelect <= 0) { // Одна строка
                firstSelect = num_active;
                for (var i = 0; i < StatusData.length; i++) {
                    if(StatusData[i].id == 'selected')
                    {
                        StatusData[i].id = 'free';
                    }
                }
                document.getElementById('workTime1').innerHTML = n.innerHTML;
                document.getElementById('workTime2').innerHTML = "....";
                getTime = true;
                n.id = 'selected';
                return;
            }
            if(num_active - firstSelect == 1)
            {
                console.log("Incorrect");
                alert("Минимальное время записи 1 час");
                n.id = 'free';
            }
            else if(num_active - firstSelect <= 3) { // Проверка границ
                console.log("Correct");
                for(var i = firstSelect - 1; i < num_active; i++)
                    if(StatusData[i].id == 'busy')
                    {
                        StatusData[num_active - 1].id = 'free';
                        alert("Ваше время пересекается с чужим");
                        return;
                    }
                for(var i = firstSelect - 1; i < num_active; i++)
                    StatusData[i].id = 'selected';
                firstSelect = -1;
                getTime = false;
                document.getElementById('workTime2').innerHTML = n.innerHTML;
                document.getElementsByName('workTime2')[0].value = n.innerHTML;
            }
            else {
                console.log("Incorrect");
                alert("Максимальное время записи 2 часа");
                n.id = 'free';
            }
        }
    }
}