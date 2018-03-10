function submitIt(url) {
  var f = document.forms["form"];
  f.method = "POST";
  f.action = url;
  f.submit();
  return true;
}
