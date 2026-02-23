function initialize_popovers() {
    const popups = document.getElementsByClassName('user_popup');
    for (let i = 0; i < popups.length; i++) {
        const popover = new bootstrap.Popover(popups[i], {
        content: 'Loading...',
        trigger: 'hover focus',
        placement: 'right',
        html: true,
        sanitize: false,
        delay: {show: 500, hide: 0},
        container: popups[i],
        customClass: 'd-inline',
        });
        popups[i].addEventListener('show.bs.popover', async (ev) => {
            if (ev.target.popupLoaded) {
                return;
            }
            const response = await fetch('/user/' + ev.target.innerText.trim() + '/popup');
            const data = await response.text();
            const popover = bootstrap.Popover.getInstance(ev.target);
            if (popover && data) {
                ev.target.popupLoaded = true;
                popover.setContent({'.popover-body': data});
                flask_moment_render_all();
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', initialize_popovers);