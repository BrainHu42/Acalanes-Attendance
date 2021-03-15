function refreshAt(hours, minutes, seconds) {
  var now = new Date();
  var then = new Date();
  if (now.getHours() > hours || now.getHours() == hours && now.getMinutes() > minutes || now.getHours() == hours && now.getMinutes() == minutes && now.getSeconds() >= seconds) {
    then.setDate(now.getDate() + 1);
  }
  then.setHours(hours);
  then.setMinutes(minutes);
  then.setSeconds(seconds);
  var timeout = then.getTime() - now.getTime();
  console.log(timeout);
  setTimeout(function() {
    if (document.getElementById("refresh")) {
      location.reload();
    }
  }, timeout);
}

function tardy_notification(hour, minute, time) {
  console.log("tardy notifications called")
  if (cookie == "yes") {
    if (time == null) {
      return;
    }
    var then = new Date();
    var now = new Date();
    then.setHours(hour);
    then.setMinutes(minute + time);
    then.setSeconds(0);
    var timeout = then.getTime() - now.getTime();
    console.log("Tardy notifications enabled.  " + timeout.toString() + " milliseconds until alert");
    if (timeout < 0) {
      return;
    }
    setTimeout(function() {
      if (document.getElementById("refresh")) {
        alert("Tardy time of " + time.toString() + " minutes reached.  Remember to update Aeries for period " + period.toString() + " now!");
      }
    }, timeout);
  }
}

function setRefresh(hour, minute) {
  tardy_notification(hour, minute, tardyTime);
  times.forEach(function(item) {
    doRefresh(hour, minute, item);
  });
}

function doRefresh(hour, minute, tardyTime) {
  var newMin = minute + tardyTime;
  if (newMin > 59) {
    hour++;
    newMin -= 60;
  }
  refreshAt(hour, newMin, Math.floor(Math.random() * 60));
}

function showDate() {
  var min, sec, hour, half;
  date.getHours() > 11 && date.getHours() < 24 ? half = " pm" : half = " am";
  date.getHours() > 12 ? hour = date.getHours() - 12 : hour = date.getHours();
  date.getSeconds() < 10 ? sec = "0" + date.getSeconds().toString() : sec = date.getSeconds().toString();
  date.getMinutes() < 10 ? min = "0" + date.getMinutes().toString() : min = date.getMinutes().toString();
  return hour.toString() + ":" + min + ":" + sec + half;
}
