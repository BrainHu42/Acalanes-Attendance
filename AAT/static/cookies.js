function get_cookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

$(document).ready(function() {
  $("#reminder").submit(function() {
    var cookieDate = new Date();
    cookieDate.setTime(cookieDate.getTime() + (365 * 24 * 60 * 60 * 1000));
    document.getElementById("remindInput").checked == true ? document.cookie = "remind=yes; expires=" + cookieDate + "; path=/;" : document.cookie = "remind=no; expires=" + cookieDate + "; path=/;"
  });
});
