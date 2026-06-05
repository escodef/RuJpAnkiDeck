import pytest
import logging
from parsers.gui_word_parser import WordParserGUI


@pytest.fixture
def parser():
    obj = WordParserGUI.__new__(WordParserGUI)
    obj.logger = logging

    return obj


def test_basic_article_ra(parser):
    test_article = """…ら
…等
суф. мн. числа; после имени собств. и другие; и его друзья (сторонники); и иже с ним, и его присные; и сопровождающие его лица.
"""

    result = parser.is_article_correct(test_article, "ら", "ラ")

    assert result is True


def test_basic_article_check(parser):
    test_article = """チェックする
1. проверять (англ. to check)
2. отмечать, помечать
3. препятствовать, тормозить"""

    result = parser.is_article_correct(test_article, "チェックする", "チェックスル")

    assert result is True


def test_basic_article_kouchiku(parser):
    test_article = """こうちく　　
構築
сооружение, постройка, строительство;
～する сооружать, строить, воздвигать."""

    result = parser.is_article_correct(test_article, "構築する", "コウチクスル")

    assert result is True


def test_basic_article_han(parser):
    test_article = """たん　　　　
反･段
1) тан (мера длины для тканей = 10,6 м);
2) тан см. <<たんぶ>>."""

    result = parser.is_article_correct(test_article, "反", "ハン")

    assert result is True


def test_yarxi_simple_article(parser):
    test_article = """東口
[higashiguchi]
восточный вход (выход)

TN57062"""

    result = parser.is_article_correct(test_article, "東口", "ヒガシグチ")

    assert result is True


def test_yarxi_simple_article_mosu(parser):
    test_article = """燃す
[mosu]
см. 燃やす [moyasu]

TN69217"""

    result = parser.is_article_correct(test_article, "モス", "モス")

    assert result is True


def test_yarxi_complex_article_mae(parser):
    test_article = """前　　　 перед
антоним 後
ZEN  qián
前 [mae] 1) перёд; ~ni впереди; ~no передний; 2) в чьём-л. присутствии, перед кем-л.; 3) ~ni раньше; ~no прежний, прошлый; 4) ~ni заранее; 5) редк., гениталии
お前まえ [o-mae] грубо ты
前々 [maemae] ~kara уже давно, задолго до чего-л.
  В сочетаниях: 
1) передний; впереди; перед чем-л. ("zen", "mae") 
前部 [zenbu] передняя часть, перёд
前輪 [zenrin] редк. [maewa] переднее колесо
前足 [maeashi] передняя нога (лапа); ср. 前脚, 前肢
駅前 [ekimae] привокзальная площадь
目前 [mokuzen] (-no) ~de (~ni) на глазах (перед глазами, под носом) у кого-л.; ср. 目の前 [me-no mae]
2) раньше чего-л. ("zen", "mae") 
以前 [izen] 1) тому назад; до; 2) ~[ni] раньше, прежде; ~no прежний, давнишний; ~kara издавна
午前 [gozen] до полудня, утром
食前 [shokuzen] до еды, перед едой
夜明け前 [yoakemae] перед рассветом
二年前 [ninenmae] два года назад
3) заранее ("zen", "mae") 
前以て [maemotte] заранее, предварительно
前払い [maebarai] предварительная оплата
前金 [maekin] [zenkin] предоплата, аванс
前文 [zenbun] 1) преамбула; 2) предыдущая фраза, вышесказанное
4) предшествующий ("zen") 
前回 [zenkai] прошлый раз; ~no прошлый, предыдущий, последний
前々回 [zenzenkai] позапрошлый (предпоследний) раз; ~no предпоследний
前記 [zenki] ~no вышеупомянутый, вышеуказанный
前条 [zenjo:] предыдущая статья (параграф, пункт)
5) порция; доля ("-mae") 
二人前 [ninin-mae] [futari-mae] ~no на двоих (порция)
6) суффикс после имён придворных дам ("-mae") 
玉藻の前 [tamamo-no-mae] госпожа Тамамо
7) идиоматические сочетания ("-mae") 
名前 [namae] имя
手前 [temae] 1) эта сторона; (-no) ~ni перед чем-л.; 2) скромно я; ~no мой; 3) грубо ты; 4) (-no) ради чего-л.; из уважения к кому-л.; принимая во внимание что-л.; 5) условия жизни, жизнь; 6) см. お手前
男前 [otokomae] красивая наружность (мужчины); ~da быть красивым
腕前 [udemae] умение, способности
気前 [kimae] великодушие, щедрость; см. 気前のいい
建前 [tatemae] 1) [декларируемые, внешние, показные] принципы; иначе 立前антоним 本音 [honne]; 2) [торжественная] закладка нового здания
当たり前 [atarimae] 1) ~[da] естественно, ничего удивительного, само собой разумеется; ~no естественный, неудивительный; правильный; заслуженный; 2) ~no обычный, обыкновенный, нормальный; ~ni как обычно, как всегда

Ключ: 刀 (刂,⺈) (18), 八 (ハ) (12). Штрихов: 9. Исп.: Гакусю (2)
Частотность: 27, JLPT: 4
Nelson: 595; New Nelson: 490; S&H: 2o7.3; Halpern: 2266; Gakken: 38; Heisig: 290; Henshall: 159
KN1614

"""

    result = parser.is_article_correct(test_article, "前", "マエ")

    assert result is True


def test_warodai_simple_article_soshite(parser):
    test_article = """そして, そうして　
союз и, тогда."""

    result = parser.is_article_correct(test_article, "そして", "ソシテ")

    assert result is True


def test_yarxi_simple_article_soshite(parser):
    test_article = """そして
[soshite], редк. [so:shite]
союз и, [и] тогда, далее; реже 然して

TN40246
"""

    result = parser.is_article_correct(test_article, "そして", "ソシテ")

    assert result is True
