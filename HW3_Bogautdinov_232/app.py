from flask import Flask
from flask import url_for, render_template, request, redirect
from models import db, ARTICLE, AUTHOR, TAG
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///archdaily.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stat')
def statistics():
    
    con = sqlite3.connect('archdaily.db')  # подключаемся
    cur = con.cursor()  # курсор

    # 1: наиболее плодотворные авторы
    cur.execute("""
        SELECT name, articlesNr
        FROM AUTHOR
        JOIN (
            SELECT authorID, COUNT(authorID) AS articlesNr 
            FROM AUTHOR_ARTICLE
            GROUP BY authorID
        ) AS stat ON AUTHOR.authorID = stat.authorID
        ORDER BY articlesNr DESC
        LIMIT 5
    """)
    result_1 = cur.fetchall()

    # 2: сколько статей было выпущено за год (со дня парсинга сайта - 1 год)?
    cur.execute("""
        SELECT COUNT(pubDate) 
        FROM ARTICLE
        WHERE pubDate > '2023-12-01'
    """)
    result_2 = cur.fetchall()

    # 3: в какой месяц выпустили больше всего статей, начиная с 22.12.2023
    cur.execute("""
        SELECT strftime('%m', pubDate) AS month, COUNT(*) AS date_count
        FROM ARTICLE
        WHERE pubDate > '2023-12-01'
        GROUP BY month
        ORDER BY date_count DESC
        LIMIT 1
    """)
    result_3 = cur.fetchall()

    # 4: наиболее популярные теги
    cur.execute("""
        SELECT name, tagsNr
        FROM TAG
        JOIN (
            SELECT tagID, COUNT(tagID) AS tagsNr 
            FROM TAG_ARTICLE
            GROUP BY tagID
        ) AS stat ON TAG.tagID = stat.tagID
        ORDER BY tagsNr DESC
        LIMIT 10
    """)
    result_4 = cur.fetchall()

    # 5: в какие дни за прошедший год авторы были наиболее щедры на теги?
    cur.execute("""
        SELECT pubDate, COUNT(pubDate) 
        FROM TAG
        JOIN TAG_ARTICLE ON TAG.tagID = TAG_ARTICLE.tagID
        JOIN ARTICLE ON ARTICLE.articleID = TAG_ARTICLE.articleID
        WHERE pubDate > '2023-12-01'
        GROUP BY pubDate
        ORDER BY COUNT(pubDate) DESC
        LIMIT 5
    """)
    result_5 = cur.fetchall()

    # 6: теги в день с наименьшим количеством использованных тегов
    cur.execute("""
        SELECT name AS tag_names_on_day_with_min_tags
        FROM TAG, TAG_ARTICLE, ARTICLE
        WHERE TAG.tagID = TAG_ARTICLE.tagID
            AND ARTICLE.articleID = TAG_ARTICLE.articleID
            AND ARTICLE.pubDate = (
                SELECT pubDate as min_tags_date 
                FROM (
                    SELECT pubDate, COUNT(pubDate) AS date_count
                    FROM TAG
                    JOIN TAG_ARTICLE ON TAG.tagID = TAG_ARTICLE.tagID
                    JOIN ARTICLE ON ARTICLE.articleID = TAG_ARTICLE.articleID
                    WHERE pubDate > '2023-12-01'
                    GROUP BY pubDate
                )
                ORDER BY date_count ASC
                LIMIT 1
            )
    """)
    result_6 = cur.fetchall()

    con.close()

    return render_template('stat.html', 
                           result_1=result_1, 
                           result_2=result_2, 
                           result_3=result_3,
                           result_4=result_4,
                           result_5=result_5,
                           result_6=result_6)

@app.route('/form')
def form():
    with open("ABBA.txt", "r", encoding='utf-8') as f:
        song = f.read().split('\n')

    return render_template('form.html', song=song)


@app.route('/process', methods=['GET'])
def answer_process():

    # если пустой запрос, то отправить проходить анкету
    if not request.args:
        return redirect(url_for('form'))

    # сразу скажу, что код в целом работает и записывает все в базу данных, но! почему-то не в ту, в которую я рассчитывал, что он будет записывать :((

    # получаем значения ответов
    article_link = request.args.get('article_link')
    article_author = request.args.get('article_author')
    article_date = request.args.get('article_date')
    article_tags = request.args.get('article_tags')
    article_text = request.args.get('article_text')
    article_title = request.args.get('article_title')

    # тут юзаем SQLAlchemy ORM, который подгрузит все в базу данных, но сначала обрабатываем результаты формы
    authors = [author.strip() for author in article_author.split(',')]
    tags = [tag.strip() for tag in article_tags.split(',')]

    # если что, вызываем ошибку, если все плохо
    try:
        # добавляем автор:ок
        for author in authors:
            new_author = AUTHOR(name=author)
            db.session.add(new_author)

        # статьи
        new_article = ARTICLE(title=article_title, pubDate=article_date, link=article_link, text=article_text)
        db.session.add(new_article)

        # и теги
        for tag in tags:
            new_tag = TAG(name=tag)
            db.session.add(new_tag)
        
        # коммитим
        db.session.commit()

    except Exception as e:
        # откатываем все назад, если где-то возникла проблема (вроде как в PostgreSQL оно автоматически умеет так делать, да?)
        db.session.rollback()
        print(f"Error: {e}")

    return 'OK'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=5005)