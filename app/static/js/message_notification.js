function set_message(n){
    const count = document.getElementById('message_count');
    count.innerText = n;
    count.style.visibility = n ? 'visibile' : 'hidden';
}