from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


# Описываем классы таблиц для бд
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# Описываем схемы сериализаторов
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    director_id = fields.Int()
    genre_id = fields.Int()
    genre = fields.Method('add_genre')
    director = fields.Method('add_director')

    def add_director(self, user):
        return user.director.name

    def add_genre(self, user):
        return user.genre.name


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# Создаем экземпляры сериализаторов
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
# Это можно удалить, нужно для теста
directors_schema = DirectorSchema(many=True)

api = Api(app)
# Создаем нэймспэйсы
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_na = api.namespace('genres')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_request = request.args.get('director_id')
        genre_request = request.args.get('genre_id')

        # Если есть квери параметры то верни запрос согласно условию
        if director_request and genre_request:
            movies = db.session.query(Movie).filter(Movie.director_id == director_request and
                                                    Movie.director_id == director_request).all()
            return movies_schema.dump(movies)

        # Если есть квери параметры то верни запрос согласно условию
        elif director_request:
            movies = db.session.query(Movie).filter(Movie.director_id == director_request).all()
            return movies_schema.dump(movies)

        # Если есть квери параметры то верни запрос согласно условию
        elif genre_request:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_request).all()
            return movies_schema.dump(movies)

        # Или просто верни список всех фильмов
        movies = db.session.query(Movie).all()
        return movies_schema.dump(movies)


@directors_ns.route('/<int:pk>')
class DirectorViews(Resource):

    # Это надо убрать, просто что бы проверить что все работает)
    def get(self, pk):
        dir = db.session.query(Director).all()
        return directors_schema.dump(dir)

    # Добавляем нового директора
    def post(self, pk):
        try:
            data = request.json
            director = Director(**data)
            db.session.add(director)
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e

    # Обновляем директора
    def put(self, pk):
        data = request.json
        try:
            director = db.session.query(Director).get(pk)
            director.id = data["id"]
            director.name = data["name"]
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e

    # Удаляем директора
    def delete(self, pk):
        try:
            director = db.session.query(Director).get(pk)
            db.session.delete(director)
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e


@genres_na.route('/<int:pk>')
class GenreViews(Resource):
    # Добавляем новый жанр
    def post(self, pk):
        try:
            data = request.json
            genre = Genre(**data)
            db.session.add(genre)
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e

    # Обновляем жанр
    def put(self, pk):
        data = request.json
        try:
            genre = db.session.query(Genre).get(pk)
            genre.id = data["id"]
            genre.name = data["name"]
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e

    # Удаляем жанр
    def delete(self, pk):
        try:
            genre = db.session.query(Genre).get(pk)
            db.session.delete(genre)
            db.session.commit()
            return app.response_class('Ok', 200)
        except Exception as e:
            return e


# Не понятно почему не получается поменять порт??
if __name__ == '__main__':
    app.run(port=8080)
