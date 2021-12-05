import HTTPResponse
import send_mail
from utils import make_hash, check_password, make_reset_token, get_reset_mail_template


class UserDbHelper:

    def __init__(self, dbconn):
        self.dbconn = dbconn
        self.cur = self.dbconn.cursor()

    def get_user_row(self, username):
        return self.cur.execute(
            "Select username, password_hash from users where username=:username",
            {"username": username}
        ).fetchone()

    def update_hash_password(self, username, hash_password):
        self.cur.execute(
            "Update users set password_hash=:password_hash where username=:username",
            {'password_hash': hash_password, 'username': username}
        )

    def add_reset_token(self, username_id, reset_token):
        self.cur.execute(
            "INSERT into resert_tokens (username_id, auth_token) "
            "values ((select id from users where username=:username),:auth_token) ",
            {'username': username_id, 'auth_token': reset_token}
        )

    def check_reset_token(self, reset_token):
        # check token if exists and not used and not expired if true mark it as used


class UserManagement:
    @staticmethod
    def authenticate(request, dbconn):
        ''' method return boolean not HTTPResponse '''
        username = request.username  # assuming that request object already provide username and password
        password = request.password
        if username is None or password is None:
            return False

        user_db = UserDbHelper(dbconn)
        user_row = user_db.get_user_row(username)

        if not user_row:
            return False

        got_password_hash = make_hash(password)
        if got_password_hash != user_row['password_hash']:
            return False

        return True

    @staticmethod
    def reset_password(request, dbconn):
        username = request.username
        user_db = UserDbHelper(dbconn)

        if request.method == "GET":
            user_row = user_db.get_user_row(username)
            reset_token = make_reset_token()
            user_db.add_reset_token(user_row["id"], reset_token)
            send_mail(to_mail=user_row['email'], body=get_reset_mail_template(reset_token))
            return HTTPResponse(200, body={"message": f"Resend link has been sent to {user_row['email']}"})

        elif request.method == "POST":
            reset_token = request.POST["reset_token"]
            if user_db.check_reset_token(reset_token):
                UserManagement.change_password(request, dbconn)
            else:
                return HTTPResponse(400, body={"message": "reset token is not valid"})

    @staticmethod
    def change_password(request, dbconn):
        # assuming request has been already authenticated
        username = request.username
        new_password = request.POST['new_password']

        if not check_password(new_password):
            return HTTPResponse(400, body={"message": "New password is not strong enough or ..."})

        new_hash_password = make_hash(new_password)

        user_db = UserDbHelper(dbconn)
        user_db.update_hash_password(username, new_hash_password)

        return HTTPResponse(201, body={"message": "password is updated successfully"})
