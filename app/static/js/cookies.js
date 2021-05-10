function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}
function eraseCookie(name) {
	var date = new Date();
    date.setTime(date.getTime() - (10*24*60*60*1000)); 
    document.cookie = name+'=; expires=' + date.toUTCString() + '; path=/';  
}

function getCookies(){
    var pairs = document.cookie.split(";");
    var cookies = {};
    for (var i=0; i<pairs.length; i++){
      var pair = pairs[i].split("=");
      cookies[(pair[0]+'').trim()] = unescape(pair.slice(1).join('='));
    }
    return cookies;
}

function deleteCookies(cookies_to_delete){
    for (const [key, value] of Object.entries(getCookies())) {
      if(key.match(cookies_to_delete)){
        console.log("deleting " + key)
        eraseCookie(key)
      }
    }
}



var ANALYSIS_COOKIES = "_g.*"; //Google Analytics

$("#more_info").on("click", function(){
    $("#extra_info_cookies_modal").modal("show");
});

$(".analysis_cookies_input").on("click", function(){
    if($(this).hasClass("checked")){
      $("#analysis_cookies").val(1);
    }else{
      $("#analysis_cookies").val(0);
    }
});  

$(".accept_cookies").on("click", function(){
    var analysis_cookies_status = $("#analysis_cookies").val();
    console.log(analysis_cookies_status)
    if(analysis_cookies_status==0){
      deleteCookies(ANALYSIS_COOKIES);
    }
    setCookie("cookies_accepted",analysis_cookies_status,365);
});

$(".reject_all").on("click", function(){
    deleteCookies(ANALYSIS_COOKIES);
    setCookie("cookies_accepted","0",365);
});

  
$(document).ready(function(){
    /* Show modal if not stored */
    if(getCookie("cookies_accepted")==null){
        $("#cookies_modal").modal("show");
    }
    /* Delete on session start */
    setTimeout(function(){
      if(getCookie("cookies_accepted")==0){
        deleteCookies(ANALYSIS_COOKIES);
      }
    },100);  
});