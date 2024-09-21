import os
from flask import Flask, send_from_directory, jsonify
from flask_jwt_extended import JWTManager
from controllers.category_controller import category_bp
from controllers.otp_controller import otp_bp
from controllers.role_controller import role_bp
from controllers.sales_report_controller import sales_report_bp
from controllers.search_controller import search_bp
from controllers.service_report_controller import service_report_bp
from controllers.spare_part_controller import spare_part_bp
from controllers.status_controller import status_bp
from controllers.store_item_controller import store_item_bp
from initializers.mysql import init_mysql, init_db
from controllers.user_controller import user_bp

app = Flask(__name__)

IMAGE_FOLDER = 'images/'

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET')

init_db(app)

jwt = JWTManager(app)

init_mysql(app)

app.register_blueprint(otp_bp)
app.register_blueprint(service_report_bp)
app.register_blueprint(search_bp)
app.register_blueprint(sales_report_bp)
app.register_blueprint(spare_part_bp)
app.register_blueprint(store_item_bp)
app.register_blueprint(category_bp)
app.register_blueprint(status_bp)
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)


@app.route('/')
def ping():
    return jsonify({"Hello!": "Welcome!"}), 200


if __name__ == "__main__":
    app.run(port=8080,debug=True)
