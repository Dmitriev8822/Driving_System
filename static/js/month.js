var monthArray = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
var today = new Date();
var years = today.getFullYear();
window.number = String(today.getMonth() + 1).padStart(2, '0') - 1;
var firstSelect = -1;
var getTime = true;
var StatusData = document.getElementsByClassName("colum");
var WeekDays = document.getElementsByClassName("0");

function image(num){
    if(num == 1){
        if(number == monthArray.length - 1)
        {
            number = -1;
            years++;
            document.getElementById('month').innerHTML = monthArray[number] + '<label>' + years + '</label>';
        }
        if(number < monthArray.length - 1){
            number++;
            document.getElementById('month').innerHTML = monthArray[number] + '<label>' + years + '</label>';
        }
    }
    else{
        if(number == 0)
        {
            number = 11;
            years--;
            document.getElementById('month').innerHTML = monthArray[number] + '<label>' + years + '</label>';
        }
        else{
            number--;
            document.getElementById('month').innerHTML = monthArray[number] + '<label>' + years + '</label>';
        }
    }
}
document.write('<div id="month" class="month__inner">' + monthArray[number] + '<label>' + years + '</label>' + '</div>');
function ButtonClick(n){
    var num_active = $(n).index(".colum") + 1; // Номер элемента
    console.log(num_active);
    if(n.id == 'selected'){
        for (var i = 0; i < StatusData.length; i++) {
            if(StatusData[i].id == 'selected')
            {
                StatusData[i].id = 'open';
            }
        }
        firstSelect = num_active;
        document.getElementsByName('workTime1')[0].value = n.innerHTML;
        document.getElementsByName('workTime2')[0].value = "....";
        getTime = true;
        n.id = 'selected';
        return;
    }
    else if(n.id != 'red')
    {
        n.id = 'selected';
        if(firstSelect == -1 && getTime) { // Выбрана ли первая граница
            firstSelect = num_active;
            document.getElementsByName('workTime1')[0].value = n.innerHTML;
        }
        else {
            if((parseInt(num_active / 28) - parseInt(firstSelect / 28) != 0) || !getTime || num_active - firstSelect <= 0) { // Одна строка
                firstSelect = num_active;
                for (var i = 0; i < StatusData.length; i++) {
                    if(StatusData[i].id == 'selected')
                    {
                        StatusData[i].id = 'open';
                    }
                }
                document.getElementsByName('workTime1')[0].value = n.innerHTML;
                document.getElementsByName('workTime2')[0].value = "....";
                document.getElementsByName('data')[0].value = "...."
                getTime = true;
                n.id = 'selected';
                return;
            }
            if(num_active - firstSelect == 1)
            {
                console.log("Incorrect");
                alert("Минимальное время записи 1 час");
                n.id = 'open';
            }
            else if(num_active - firstSelect <= 3) { // Проверка границ
                console.log("Correct");
                for(var i = firstSelect - 1; i < num_active; i++)
                    if(StatusData[i].id == 'red')
                    {
                        StatusData[num_active - 1].id = 'open';
                        alert("Ваше время пересекается с чужим");
                        return;
                    }
                for(var i = firstSelect - 1; i < num_active; i++)
                    StatusData[i].id = 'selected';
                document.getElementsByName('data')[0].value = WeekDays[parseInt(num_active / 28)].id;
                firstSelect = -1;
                getTime = false;
                document.getElementsByName('workTime2')[0].value = n.innerHTML;
            }
            else {
                console.log("Incorrect");
                alert("Максимальное время записи 2 часа");
                n.id = 'open';
            }
        }
    }
}