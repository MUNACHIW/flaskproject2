from flask import Flask, render_template, request, redirect, session, flash,url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import timedelta,datetime
import os
import random
import time 
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.sql.expression import or_
from flask_socketio import SocketIO , join_room, leave_room, send
from string import ascii_uppercase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///face.db'
app.secret_key = "QFMF3KFK3OKOKOELPDMDL0---W388403--2"
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
socketio = SocketIO(app)



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] =587
app.config['MAIL_USERNAME'] = 'c02474094@gmail.com'
app.config['MAIL_PASSWORD'] = 'ahyvweniwvpghfqw'
app.config['MAIL_USE_TLS'] =  True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOAD_POST'] = 'static/video'
mail = Mail(app)
s = URLSafeTimedSerializer('Thisisasecret!')


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=False)
    surname = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    birth = db.Column(db.Integer, nullable = False)
    gender = db.Column(db.String, nullable = True)
    online = db.Column(db.Boolean, nullable=False, default=False)
    updates = db.relationship('Update', backref='user', lazy=True)
    covers = db.relationship('Cover', backref='user', lazy=True)
    video = db.relationship('Video', backref= 'user', lazy= True )
    friends = db.relationship('Friendship', foreign_keys='Friendship.user_id', backref='user_friend', lazy='dynamic')
    profile_pic = db.Column(db.String)
    def __str__(self):
        return '<User %r>' % self.username


class Update(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    profile_pic = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    like = db.relationship('UpdateLike', backref = 'update', lazy= True)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_id = db.Column(db.Integer, db.ForeignKey('update.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable = True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Comment('{self.text}', '{self.timestamp}')"

    
class UpdateLike(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_id = db.Column(db.Integer, db.ForeignKey('update.id'), nullable=False)

    def __str__(self):
        return self.update_id
class Cover(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cover_pic = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    like = db.relationship('CoverLike', backref = 'cover', lazy = True)
    
class CoverLike(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    cover_id = db.Column(db.Integer, db.ForeignKey('cover.id'), nullable = False)
    
    def __str__(self):
        return self.cover_id
    
class Video(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    profile_pic = db.Column(db.String, nullable = True)
    like =  db.relationship('VideoLike', backref = 'video', lazy = True)
    
    
class VideoLike(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable = False)
    
    def __str__(self):
        return self.video_id

class Friendship(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    accepted = db.Column(db.Boolean, default=False) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", foreign_keys=[user_id], backref="friendship_user")
    friend = db.relationship("User", foreign_keys=[friend_id], backref="friendship_friend")


    
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60.0)







@app.route('/')
def index():
    if not session.get('user'):
        return redirect("/signin")
    
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    username = user.username
    
    friendships = Friendship.query.filter_by(user_id=user.id, accepted=True).all()
    friend_ids = [friendship.friend_id for friendship in friendships]
    
    
    online_friends = User.query.filter(User.id.in_(friend_ids), User.online==True).all()

    profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()
    # Get the user's friends
    friendships = Friendship.query.filter((Friendship.user_id==user.id) | (Friendship.friend_id==user.id), Friendship.accepted==True).all()
    friend_ids = [friendship.user_id if friendship.user_id != user.id else friendship.friend_id for friendship in friendships]

    # Only show updates from friends
    profile_updates = Update.query.filter(Update.user_id.in_(friend_ids)).order_by(Update.timestamp.desc()).all()
    updates = Update.query.filter(Update.user_id.in_(friend_ids)).all()
    current_time = datetime.utcnow() # Get the current time
    profile_pic_size = 480 
    
    profile_info = []
    for update in updates:
        # Get the user who made the update
        update_user = User.query.filter_by(id=update.user_id).first()
        if datetime.now() - update.timestamp <= timedelta(minutes=5):
            profile_info.append(f'{update_user.username} updated profile picture at')
            print(f"{update_user.username} newly updated profile picture at {update.timestamp}")
        else:
              profile_info.append(f'{update_user.username} updated profile picture at') 
    
    # Only show covers from friends
    covers = Cover.query.filter(Cover.user_id.in_(friend_ids)).order_by(Cover.timestamp.desc()).all()
    cover_info = []
    for cover in covers:
    # Get the user who made the update
      cover_user = User.query.filter_by(id=cover.user_id).first()
      if datetime.now() - cover.timestamp <= timedelta(minutes=5):
        cover_info.append(f'{cover_user.username} newly updated Cover photo at')
        print(f"User {cover_user.username} updated their cover at {cover.timestamp}")
      else:
            cover_info.append(f'{cover_user.username} updated Cover photo at {cover.timestamp}')
            
    videoquery =Video.query.order_by(Video.timestamp.desc()).all()
    #Getting the user that made the video post
    video_info = []
    for video in videoquery :
        video_user = User.query.filter_by(id = video.user_id).first()
        if datetime.now() - video.timestamp <= timedelta(minutes=5):
             video_info.append(f'{video_user.username} uploaded video at {video.timestamp}')
             print(f"User {video_user.username} uploaded their video at {video.timestamp}")
             
             
    if not user:
        return jsonify({'message': 'User not found'}), 404
    friend_requests = Friendship.query.filter_by(friend_id=user.id, accepted=False).all()
    friend_requests_data = []
    for fr in friend_requests:
     try:
        profile_pic = Update.query.filter_by(user_id=fr.user_id).order_by(Update.timestamp.desc()).first().profile_pic
        friend_requests_data.append({'request_id': fr.request_id, 'user_id': fr.user_id, 'username': fr.user.username, 'profile_pic': profile_pic})
     except:
                 friend_requests_data.append({'request_id': fr.request_id, 'user_id': fr.user_id, 'username': fr.user.username}) 
    likes = 0
    updates_likes = []
    # Define updates here
    updates = Update.query.all()  # or any other query that fits your needs
    if updates:
        for update in updates:
            likes = UpdateLike.query.filter_by(update_id=update.id).count()
            updates_likes.append({'update_id': update.id, 'likes': likes})
    else:
        update = None
    comment = Comment.query.filter_by(update_id=update.id).order_by(Comment.timestamp.desc()).all()

    return render_template('index.html',  updates_likes=updates_likes, update = update, likes = likes, user=user, timedelta=timedelta, username=username, online_friends=online_friends,
                           profile=profile, profile_updates=profile_updates, current_time=current_time, datetime = datetime, comment = comment,
                            updates=updates, covers=covers, profile_info=profile_info, cover_info = cover_info, profile_pic_size =
                            profile_pic_size, user_id = user.id, video_info =video_info, videoquery =videoquery, friend_requests=friend_requests_data )
rooms = {}  
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
        
    return code

@app.route("/message", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")
  

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    
    return render_template("room.html", code=room) 

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")
    
@socketio.on("connect")  
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message":"has entered the room"}, to = room)
    rooms[room]["members"]+=1
    print(f"{name} joined room {room}")    
    
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    if room in rooms:
        rooms[room]["members"]-= 1
        if rooms[room]["members"]<= 0:
            del rooms[room]
    send({"name": name, "message":"has left the room"}, to = room)
    print(f"{name} has left the room {room}")    
    
@app.route('/commentdetails/<int:update_id>', methods=['GET', 'POST'])
def commentdetails(update_id):
    if not session.get('user'):
        return redirect("/signin")

    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    friendships = Friendship.query.filter_by(user_id=user.id, accepted=True).all()
    friend_ids = [friendship.friend_id for friendship in friendships]
    
    
    online_friends = User.query.filter(User.id.in_(friend_ids), User.online==True).all()

    profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()
    # Get the user's friends
    friendships = Friendship.query.filter((Friendship.user_id==user.id) | (Friendship.friend_id==user.id), Friendship.accepted==True).all()
    friend_ids = [friendship.user_id if friendship.user_id != user.id else friendship.friend_id for friendship in friendships]

    profile_updates = Update.query.filter(Update.user_id.in_(friend_ids)).order_by(Update.timestamp.desc()).first()
    updates = Update.query.filter(Update.user_id.in_(friend_ids)).all()
    comment = Comment.query.filter_by(update_id=update_id).order_by(Comment.timestamp.desc()).all()
    current_time = datetime.utcnow() # Get the current time
    profile_pic_size = 480 
    
    profile_info = []
    for update in updates:
        # Get the user who made the update
        update_user = User.query.filter_by(id=update.user_id).first()
        if datetime.now() - update.timestamp <= timedelta(minutes=5):
            profile_info.append(f'{update_user.username} updated profile picture at')
            print(f"{update_user.username} newly updated profile picture at {update.timestamp}")
        else:
              profile_info.append(f'{update_user.username} updated profile picture at') 
  
    update = Update.query.get(update_id)
    if update is None:
        flash('Update not found.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        comment_text = request.form.get('comment')
        profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()
        profile_pic =  profile.profile_pic
        try: 
            new_comment = Comment(user_id=user.id, update_id=update_id, text=comment_text, profile_pic = profile_pic, )
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been posted.')
        except  None:
            new_comment = Comment(user_id=user.id, update_id=update_id, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been posted.')
        except AttributeError:
            new_comment = Comment(user_id=user.id, update_id=update_id, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been posted.')
            
            
        return redirect(url_for('commentdetails', update_id=update_id))

    comments = Comment.query.filter_by(update_id=update_id).order_by(Comment.timestamp.desc()).all()
    return render_template('comment.html', user=user, update=update,timedelta = timedelta, datetime =datetime, user_id = user.id, current_time = current_time, profile_pic_size = profile_pic_size,
                            profile = profile, profile_updates = profile_updates , comments = comments, profile_info =profile_info, comment = comment, 
                           )






@app.route("/upload_vid", methods=['POST'])
def upload_file():
    file = request.files.get("filename")
    if not file:
        return "No selected file"
    if not file.filename:
        return "No selected file"
    if not allowed_video(file.filename):
        return "Invalid file type"
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_POST'], filename))
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    now = datetime.now()
    profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()
    profile_pic = None if profile is None else profile.profile_pic
    if profile_pic is None:
        profile_pic = None
        video = Video(user_id=user.id, filename=filename, timestamp=now)
        db.session.add(video)
        db.session.commit()
        return redirect("/")
    else:
        profile_pic = profile.profile_pic
        video = Video(user_id=user.id, filename=filename, timestamp=now, profile_pic=profile_pic)
        db.session.add(video)
        db.session.commit()
        return redirect("/")
        
def allowed_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'mp4', 'mkv'}

  
  
@app.route("/video", methods=['GET', 'POST'])
def videos():
   videoquery =Video.query.order_by(Video.timestamp.desc()).all()  
   return render_template("video.html", videoquery = videoquery)
 
   


@app.route('/search')
def search():
    input = request.args.get('input') # get the user input from the query parameter
    results = User.query.filter(User.username.like('%' + input + '%')).all() # find the matching users
    users = [] # create a list to store the user data
    for user in results:
        users.append({'id': user.id, 'username': user.username, 'surname': user.surname}) # append a dictionary for each user
    return jsonify(users) # return the list as a JSON response
app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users])

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        data = request.form
        username = data['username']
        surname = data['surname']
        email = data['email']
        password = data['password']
        security = generate_password_hash(password)
        birth = data['date']
        gender = data['gender'] 
        birth_date = datetime.strptime(birth, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
         # Check if the user is at least 16 years old
        if age < 13:
            flash("You must be at least 13 years old to sign up.") 
            return redirect("/signup")
        if not username or not surname or not email or not password or not birth:
            flash("Please fill in all fields.")
            return redirect("/signup")
        
        if password.strip() == "":
             flash("Please fill in password with valid content.")
        
        
        user = User(username = username, surname = surname, email = email , password = security, birth = birth,  gender = gender )
        username_query = User.query.filter_by(username = username).first()
        email_query = User.query.filter_by(email = email).first()
        if username_query or email_query:
            flash('It seems username or email already exist try login or signup with another name or username with abstraction(#)')
            return redirect('/signup')
            
        db.session.add(user)
        db.session.commit()
        return redirect("/")
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
@app.route("/update",methods = ['POST'])
def update():
    if not session.get('user'):
        return redirect("/signin")
    if request.method == "POST":
        file = request.files['file']
        if not file:
            return redirect("/profile")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logged_in_user = session.get("user")
        user = User.query.filter_by(username=logged_in_user['username']).first()
        
        # Add a timestamp to each profile update
        now = datetime.now()
        profile = Update(user_id=user.id, profile_pic=filename,  timestamp=now)
        db.session.add(profile)
        db.session.commit()

        # Flash the message only for the newly updated profile picture
        # if datetime.now() - profile.timestamp <= timedelta(minutes=5):
        #     # flash(f'{user.username} newly updated profile picture: {filename}')
        return redirect("/profile")
    
from flask import jsonify

@app.route('/like/<int:update_id>', methods=['POST'])
def like(update_id):
    if 'user_id' in session:
        user_id = session['user_id']
        update_like = UpdateLike.query.filter_by(user_id=user_id, update_id=update_id).first()
        if update_like:
            db.session.delete(update_like)
        else:
            update_like = UpdateLike(user_id=user_id, update_id=update_id)
            db.session.add(update_like)
        db.session.commit()

        # Get the new like count
        new_like_count = UpdateLike.query.filter_by(update_id=update_id).count()
        return jsonify({'new_like_count': new_like_count})

    return redirect(url_for('index'))










@app.route('/like_count/<int:update_id>')
def like_count(update_id):
    count = UpdateLike.query.filter_by(update_id=update_id).count()
    return str(count)




# @app.route('/add_friend/<int:friend_id>', methods=['POST'])
# def add_friend(friend_id):
#     if not session.get('user'):
#         return redirect("/signin")
#     logged_in_user = session.get("user")
#     user = User.query.filter_by(username=logged_in_user['username']).first()
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
#     friend = User.query.get(friend_id)
#     if not friend:
#         return jsonify({'message': 'Friend not found'}), 404
#     if user == friend:
#         return jsonify({'message': 'You cannot befriend yourself'}), 400
#     friendship = Friendship.query.filter_by(user_id=user.id, friend_id=friend.id).first()
#     if friendship:
#         if friendship.accepted:
#             return jsonify({'message': 'Friendship already exists'}), 400
#         else:
#             return jsonify({'message': 'Friend request already sent'}), 400
#     max_request_id = db.session.query(db.func.max(Friendship.request_id)).scalar()
#     request_id = max_request_id + 1 if max_request_id is not None else 1
#     friendship = Friendship(request_id=request_id, user_id=user.id, friend_id=friend.id, accepted=False)
#     db.session.add(friendship)
#     db.session.commit()
#     return jsonify({'message': f'Friend request sent to {friend.username}'}), 200
@app.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    if not session.get('user'):
        return redirect("/signin")
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    friend = User.query.get(friend_id)
    if not friend:
        return jsonify({'message': 'Friend not found'}), 404
    if user == friend:
        return jsonify({'message': 'You cannot befriend yourself'}), 400
    # Check for existing friendship or friend request in either direction
    existing_friendship = Friendship.query.filter(
        (Friendship.user_id == user.id) & (Friendship.friend_id == friend.id) |
        (Friendship.user_id == friend.id) & (Friendship.friend_id == user.id)
    ).first()
    if existing_friendship:
        if existing_friendship.accepted:
            return jsonify({'message': 'Friendship already exists'}), 400
        else:
            return jsonify({'message': 'Friend request already sent'}), 400
    max_request_id = db.session.query(db.func.max(Friendship.request_id)).scalar()
    request_id = max_request_id + 1 if max_request_id is not None else 1
    new_friendship = Friendship(request_id=request_id, user_id=user.id, friend_id=friend.id, accepted=False)
    db.session.add(new_friendship)
    db.session.commit()
    return jsonify({'message': f'Friend request sent to {friend.username}'}), 200


@app.route('/friend_requests', methods=['GET', 'POST'])
def view_friend_requests():
    if not session.get('user'):
        return redirect("/signin")
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    friend_requests = Friendship.query.filter_by(friend_id=user.id, accepted=False).all()
    friend_requests_data = []
    for fr in friend_requests:
        try:
          profile_pic = Update.query.filter_by(user_id=fr.user_id).order_by(Update.timestamp.desc()).first().profile_pic
          friend_requests_data.append({'request_id': fr.request_id, 'user_id': fr.user_id, 'username': fr.user.username, 'profile_pic': profile_pic})
        except:
         friend_requests_data.append({'request_id': fr.request_id, 'user_id': fr.user_id, 'username': fr.user.username})
    return render_template('friend_requests.html', friend_requests=friend_requests_data)




@app.route('/friends/<int:user_id>')
def friends(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    friendships = Friendship.query.filter_by(user_id=user.id, accepted=True).all()
    friends_data = []
    for fr in friendships:
        profile_pic = None
        if fr.friend.updates:
            profile_pic = fr.friend.updates[-1].profile_pic  # Get the latest update's profile_pic
        friends_data.append({'friend_id': fr.friend_id, 'username': fr.friend.username, 'profile' : profile_pic})
  
    return render_template('friends.html', friends=friends_data)


 
@app.route('/respond_friend_request/<int:request_id>', methods=['POST'])
def respond_friend_request(request_id):
    if not session.get('user'):
        return redirect("/signin")
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    friend_request = Friendship.query.filter_by(request_id=request_id, friend_id=user.id).first()
    if not friend_request:
        return jsonify({'message': 'Friend request not found'}), 404
    response = request.form.get('response')
    if response == 'accept':
        friend_request.accepted = True
        db.session.commit()
        return jsonify({'message': 'Friend request accepted'}), 200
    elif response == 'reject':
        db.session.delete(friend_request)
        db.session.commit()
        return jsonify({'message': 'Friend request rejected'}), 200
    else:
        return jsonify({'message': 'Invalid response'}), 400


@app.route('/updatecover', methods = ['POST'])
def cover():
    if not session.get('user'):
        return redirect("/signin")
    if request.method == 'POST':
        file = request.files['cover']
        if not file:
            return redirect("/profile")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logged_in_user = session.get("user")
        user = User.query.filter_by(username=logged_in_user['username']).first()
        cover = Cover(user_id=user.id, cover_pic=filename)
        db.session.add(cover)
        db.session.commit()
        return redirect("/profile")

        
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
@app.route("/profile")
def profile():
    if not session.get('user'):
        return redirect("/signin")
    
    logged_in_user = session.get("user")
    user = User.query.filter_by(username=logged_in_user['username']).first()
    profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()
    cover = Cover.query.filter_by(user_id=user.id).order_by(Cover.timestamp.desc()).first()
    
    
    friendships = Friendship.query.filter_by(user_id=user.id, accepted=True).all()
    friend_ids = [friendship.friend_id for friendship in friendships]
    
    
    online_friends = User.query.filter(User.id.in_(friend_ids), User.online==True).all()

    profile = Update.query.filter_by(user_id=user.id).order_by(Update.timestamp.desc()).first()

    # Get the user's friends
    friendships = Friendship.query.filter((Friendship.user_id==user.id) | (Friendship.friend_id==user.id), Friendship.accepted==True).all()
    friend_ids = [friendship.user_id if friendship.user_id != user.id else friendship.friend_id for friendship in friendships]

    # Only show updates from friends
    profile_updates = Update.query.filter(Update.user_id.in_(friend_ids)).order_by(Update.timestamp.desc()).all()
    updates = Update.query.filter(Update.user_id.in_(friend_ids)).all()
    current_time = datetime.utcnow() # Get the current time
    profile_pic_size = 480 
    
    profile_info = []
    for update in updates:
        # Get the user who made the update
        update_user = User.query.filter_by(id=update.user_id).first()
        if datetime.now() - update.timestamp <= timedelta(minutes=5):
            profile_info.append(f'{update_user.username} updated profile picture at')
            print(f"{update_user.username} newly updated profile picture at {update.timestamp}")
        else:
              profile_info.append(f'{update_user.username} updated profile picture at') 
    
    # Only show covers from friends
    covers = Cover.query.filter(Cover.user_id.in_(friend_ids)).order_by(Cover.timestamp.desc()).all()
    cover_info = []
    for cover in covers:
    # Get the user who made the update
      cover_user = User.query.filter_by(id=cover.user_id).first()
      if datetime.now() - cover.timestamp <= timedelta(minutes=5):
        cover_info.append(f'{cover_user.username} newly updated Cover photo at')
        print(f"User {cover_user.username} updated their cover at {cover.timestamp}")
      else:
            cover_info.append(f'{cover_user.username} updated Cover photo at {cover.timestamp}')
    videoquery = Video.query.order_by(Video.timestamp.desc()).all()
    
    return render_template('profile.html', user=user, profile=profile, cover=cover, profile_pic_size = profile_pic_size,
                           profile_updates =profile_updates, current_time = current_time , profile_info =profile_info, 
                            covers =covers, cover_info = cover_info, videoquery  = videoquery)

        
    


@app.route('/users', methods=['GET'])
def get_users():
    if not session.get('user'):
        return redirect("/signin")
    logged_in_user = session.get("user")
    users = User.query.filter(User.username != logged_in_user['username']).all()
    profile = Update.query.order_by(Update.timestamp.desc()).first()
    return render_template('users.html', users=users, profile = profile)




@app.route("/signin", methods=['GET',"POST"])
def handle_signin():
    if  session.get('user'):
        flash("User is still logged in")
        return redirect("/")
    if request.method == "GET":
        return render_template("signin.html")
    
    if request.method == "POST": 
        data = request.form
        username = data['username']
        password = data['password']
        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        
        if user  is None:
            flash("User does not exist")
            # Redirect the user back to the signup page
            return redirect("/signup")
        if check_password_hash(user.password, password):
            session['user'] = {
                "username": user.username
            }
            user.online = True
            logged_in_user = session.get('user')
            user = User.query.filter_by(username=logged_in_user['username']).first()
            email = user.email
         
            # msg = Message('Hello', sender = 'c02474094@gmail.com', recipients = [email])
            # msg.body = "Hello " + username + ", thank you for logging in to MONRCH!"
            # mail.send(msg)
            return redirect("/")
        flash("You are not logged in")
        return redirect("/signin")

    
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)
            return redirect(url_for('reset_password', token=token))
        else:
            flash("This email does not exist!")
            return redirect(url_for('forgot_password' ))
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash('<h1>The token is expired!</h1>')
        return redirect("")
    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        user.password = generate_password_hash(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('/'))
    return render_template('reset_password.html')
     
     
@app.route('/logout')
def logout():
  if session.get("user"):
      logged_in_user = session.get("user")
      user = User.query.filter_by(username=logged_in_user['username']).first()
    # Set the user's online attribute to False
      user.online = False
      if logged_in_user is None:
          session.clear()
          flash("You have logged out successfully")
          db.session.commit()
          return redirect("/signin")
    # Clear the session
      session.clear()
      flash("You have logged out successfully")
      db.session.commit()
      return redirect("/signin")
 
 
 
 
# while True:
#    time.sleep(1) # this will pause the program for 1 second
#    print("BREAK") # th   


if __name__ == "__main__":
 socketio.run(app, port=3000, debug=True) 