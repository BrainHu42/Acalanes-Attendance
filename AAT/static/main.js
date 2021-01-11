$(document).ready(function() {
  function showDate() {
    var date = new Date();
    var min, sec, hour, half;
    date.getHours() > 11 && date.getHours() < 24 ? half = " pm" : half = " am";
    date.getHours() > 12 ? hour = date.getHours() - 12 : hour = date.getHours();
    date.getSeconds() < 10 ? sec = '0' + date.getSeconds().toString() : sec = date.getSeconds().toString();
    date.getMinutes() < 10 ? min = '0' + date.getMinutes().toString() : min = date.getMinutes().toString();
    return hour.toString() + ':' + min + ':' + sec + half;
  }

  $("#date").html(showDate());

  if ($("#absent").children().length == 1) {
    $("#absent").append("<p class='center' style='font-size: 14px;'><em>No absences!</em></p>");
  }
  if ($("#tardy").children().length == 1) {
    $("#tardy").append("<p class='center' style='font-size: 14px;'><em>No tardies yet!</em></p>");
  }
  if ($("#strangerArea").children().length == 0) {
    $("#strangerArea").append("<p class='center'><em>No strangers yet!</em></p>");
  }

  $("#refresh").click(function() {
    location.reload();
  });

  $("#reminder").submit(function() {
    var cookieDate = new Date();
    cookieDate.setTime(cookieDate.getTime() + (365 * 24 * 60 * 60 * 1000));
    document.getElementById("remindInput").checked == true ? document.cookie = "remind=yes; expires=" + cookieDate + "; path=/;" : document.cookie = "remind=no; expires=" + cookieDate + "; path=/;"
  });
});
