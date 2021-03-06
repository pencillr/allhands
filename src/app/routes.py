from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, SearchForm, ChooseShip
from app.models import User, Post
from datetime import datetime
from werkzeug.urls import url_parse
from app.simulator.runner import Runner


@app.before_request
def defore_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            author=current_user,
            ship_name=form.ship_name.data,
            ship_type=int(form.ship_type.data)
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    next_url = None
    prev_url = None
    if search_form.validate_on_submit():
        redirect(request.path)
        found = False
        posts = []
        all_posts = Post.query.order_by(Post.timestamp.desc()).all()
        for pst in all_posts:
            if pst.ship_name and search_form.q.data.lower() in pst.ship_name.lower():
                posts.append(pst)
                found = True
        if not found:
            flash('Ship not found!')
        else:
            total = len(posts)
            next_url = url_for('explore', page=page + 1) \
                if total > page * app.config['POSTS_PER_PAGE'] else None
            prev_url = url_for('explore', page=page - 1) \
                if page > 1 else None
    else:
        paginated = Post.query.order_by(Post.timestamp.desc()).paginate(
                page, app.config['POSTS_PER_PAGE'], False)
        next_url = url_for('explore', page=paginated.next_num) \
            if paginated.has_next else None
        prev_url = url_for('explore', page=paginated.prev_num) \
            if paginated.has_prev else None
        posts = paginated.items
    return render_template("index.html", title='Explore', posts=posts,
                          next_url=next_url, prev_url=prev_url, search=search_form)


@app.route('/fight/<ship_name>', methods=['GET', 'POST'])
@login_required
def fight(ship_name):
    ship = Post.query.filter_by(ship_name=ship_name).first_or_404()
    if current_user == ship.author:
        flash("Cannot attack your own ships!")
        return redirect(url_for('index'))
    form = ChooseShip()
    form.ship.choices = [(s.ship_name, s.ship_name) for s in Post.query.filter_by(author=current_user)]
    if form.validate_on_submit():
        flash("You chose {}".format(form.ship.data))
        own_ship = Post.query.filter_by(ship_name=form.ship.data).first()
        runner = Runner()
        runner.add_sheet(ship.ship_type, ship.ship_name, ship.gunner_agility, ship.helmsman_agility)
        runner.add_sheet(own_ship.ship_type, own_ship.ship_name, own_ship.gunner_agility, own_ship.helmsman_agility)
        looser = runner.run()
        session['report'] = runner.report.get_reports()
        if looser != own_ship.ship_name:
            return redirect(url_for('get_result', looser=looser))
        return redirect(url_for('get_result', looser=looser))
    return render_template("fight.html", title='Fight', enemy=ship, form=form)


@app.route('/result/lost:<looser>')
@login_required
def get_result(looser):
    report = session['report']
    session.pop('report', None)
    return render_template("result.html", title='Result', looser=looser, report=report)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)