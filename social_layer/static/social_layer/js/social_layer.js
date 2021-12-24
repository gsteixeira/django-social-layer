
// Reply to a comment
function reply_to(comment_id){
    var form_name = 'rt_form_'+comment_id;
    console.log(form_name);
    var forms = document.getElementsByTagName('form');
    for (i=0; i<forms.length; i++){
        if (forms[i].id.indexOf('rt_form_') > -1){
            forms[i].innerHTML = '';
            forms[i].style.display = 'none';
        }
    }
    document.getElementById(form_name).innerHTML = document.getElementById('reply-mod').innerHTML;
    document.getElementById(form_name).style.display = 'block';
}

// Perform the like button action
function sl_like(url, div_result){
    var xhttp = new XMLHttpRequest();
    xhttp.addEventListener("loadend", function(){
        document.getElementById(div_result).innerHTML = this.responseText;
    });
    xhttp.open("GET", url, async=true);
    xhttp.send();
}

// Invites the user to register at the site
function log_2join(elm, url){
    var current_url = window.location.href;
    window.location = url + '?next=' + current_url;
}
