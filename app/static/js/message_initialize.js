function initialize_notifications() {
    let since = 0;
    setInterval(async function(){
        // ignore red lines on main.notifications since its jinja template
        const response = await fetch('{{ url_for('main.notifications') }}?since=' + since);
        const notifications = await response.json();
        for (let i = 0; i < notifications.lenth; i++){
            if (notifications[i].name == 'unread_message_count')
                set_message_count(notifications[i].data);
            since = notifications[i].timestamp;
        }
    }, 10000)
}
document.addEventListener('DOMContentLoaded', initialize_notifications);