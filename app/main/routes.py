from datetime import datetime, timezone
from flask import request, session, render_template, flash, redirect, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, MessageForm, CommentForm
from app.models import User, Post, Message, Notification, Like, Post, Comment
from app.main import bp
from flask import jsonify


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    comment_form = CommentForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, comment_form=comment_form)

@bp.route('/explore')
@login_required
def explore():
    comment_form = CommentForm()
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, comment_form=comment_form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    comment_form = CommentForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form, comment_form=comment_form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    comment_form = CommentForm()
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form, comment_form=comment_form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/change_language/<lang>')
def change_language(lang):
    if lang in current_app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)

@bp.route('/send_message/<recipient>', methods=['POST', 'GET'])
@login_required
def send_message(recipient):
    user = db.first_or_404(sa.select(User).where(User.username == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        user.add_notification('unread_message_count', user.unread_message_count())
        db.session.add(msg)
        db.session.commit()
        flash(_('Your Message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'), form=form, recipient=recipient)

@bp.route('/messages')
@login_required
def messages():
    # reset unread count
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    # get distinct users you have exchanged messages with
    users = db.session.scalars(
        sa.select(User)
        .join(Message, sa.or_(
            Message.sender_id == User.id,
            Message.recipient_id == User.id
        ))
        .where(
            sa.or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id
            )
        )
        .distinct()
    ).all()

    return render_template('messages.html', users=users)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    notifications = db.session.scalars(query)
    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications]

@bp.route('/conversation/<username>', methods=['GET', 'POST'])
@login_required
def conversation(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.unread_message_count())
        db.session.commit()
        return redirect(url_for('main.conversation', username=username))

    # fetch both sent and received messages between the two users
    messages = db.session.scalars(
        sa.select(Message)
        .where(
            sa.or_(
                sa.and_(Message.sender_id == current_user.id,
                        Message.recipient_id == user.id),
                sa.and_(Message.sender_id == user.id,
                        Message.recipient_id == current_user.id)
            )
        )
        .order_by(Message.timestamp.asc())
    ).all()

    return render_template('conversation.html', user=user, messages=messages, form=form)

@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = db.get_or_404(Post, post_id)

    existing = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({
            "liked": False,
            "count": post.like_count()
        })
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({
            "liked": True,
            "count": post.like_count()
        })
    
@bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = db.get_or_404(Post, post_id)
    body = request.form.get('body')

    if body:
        comment = Comment(
            body=body,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()

    return redirect(request.referrer or url_for('main.index'))

# for testing email error
# @bp.route('/test-error')
# def test_error():
#     1 / 0  # This will crash the app intentionally