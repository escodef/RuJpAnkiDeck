import pytest

from parsers.gui_word_parser import WordParserGUI
from models.models import Translation


@pytest.fixture
def parser():
    obj = WordParserGUI.__new__(WordParserGUI)
    return obj


def test_basic_article_ra(parser):
    test_articles_ra = [
        """…ら
…等
суф. мн. числа; после имени собств. и другие; и его друзья (сторонники); и иже с ним, и его присные; и сопровождающие его лица.
"""
    ]

    results = parser.process_results(test_articles_ra)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "…等"
    assert first_res.reading == "…ら"
    assert first_res.mainsense == "суф. мн. числа"


def test_basic_article_hani(parser):
    test_articles_hani = [
        """はんい
範囲
сфера, область, круг; диапазон; радиус [действий]; предел;
我々の範囲では в нашем кругу;
私の知る範囲では насколько мне известно;
範囲を限る ставить [определённые] рамки чему-л., ограничивать пределы чего-л.;
人智の範囲を越える быть за пределами человеческих знаний;
彼の読書の範囲は広い круг (диапазон) его чтения широк."""
    ]

    results = parser.process_results(test_articles_hani)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "範囲"
    assert first_res.reading == "はんい"
    assert first_res.mainsense == "сфера, область, круг"


def test_basic_article_shindan(parser):
    test_articles = [
        """しんだん
診断
диагноз;
～する, 診断を下す ставить диагноз;
医者には診断がつかなかった врач не мог поставить диагноза."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "診断"
    assert first_res.reading == "しんだん"
    assert first_res.mainsense == "диагноз"


def test_list_article_beshi(parser):
    test_articles = [
        """べし
可し
1. нужно, следует (делать и т.п.)
2. должно быть, вероятно"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "可し"
    assert first_res.reading == "べし"
    assert first_res.mainsense == "нужно, следует (делать и т.п.)"


def test_list_article_tokoro(parser):
    test_articles = [
        """ところ
所I･処
сущ.
1) место;
…～にある находиться где-л.;
…する所がない негде сделать что-л.;
所かまわず безразлично где (в каком месте), в любом месте;
所によって異なる различаться в зависимости от места (от того, где находится);
彼の行っている所が分からない я не знаю, куда он ушёл (уехал); я не знаю, где он;
人のいる所 в присутствии людей; при людях;
その町は海抜二千フィートの所にある этот город расположен на высоте 2000 футов над уровнем моря;
2) [определённое] место;
所を得る быть на [своём] месте;
物には所がある всему своё место;
3) местожительство; чей-л. дом;
所を教える объяснять, где живёшь, давать свой адрес;
私の所に у меня [дома];
伊東の所に行く пойти к г-ну Ито́;
伊東さんの所のお嬢さん дочь г-на Ито́;
おじの所にいる жить у дяди;
ぼくの所は家族が多い у меня большая семья;
4) перен. место, сторона; черты;
弱い所 слабое место, слабая сторона;
いい所がある есть положительные стороны (моменты);
彼らは見る所が異なる у них разные точки зрения, они смотрят с разных точек зрения;
5) кое-что, что-то; то что;
君の言う所 то, что ты говоришь;
それが私の望む所だ вот чего мне хочется, вот на что я надеюсь;
この事にもっともらしい所もある в этом есть кое-что правдоподобное;
彼は学者らしい所がある в нём есть что-то от учёного;
彼女には女らしい所がない в ней нет ничего женственного;
…は周知の所である что-л. общеизвестно; общеизвестно, что…;
君の知る所ではない это не твоё дело;
私の見た所では по тому, что я видел…; насколько я видел;
私の知っている所で насколько мне известно, насколько я знаю."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "所I･処"
    assert first_res.reading == "ところ"
    assert first_res.mainsense == "место"


def test_list_article_dzukuri(parser):
    test_articles = [
        """…づくり
…造り
построенный из чего-л.;
煉瓦造りの кирпичный."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "…造り"
    assert first_res.reading == "…づくり"
    assert first_res.mainsense == "построенный из чего-л."
    assert (
        first_res.senses
        == """построенный из чего-л.;
煉瓦造りの кирпичный."""
    )


def test_list_article_mame(parser):
    test_articles = [
        """まめ　　　　
まめ･忠実
1): ～な честный, преданный;
まめに勤める честно служить;
2): ～な старательный, усердный;
まめに働く усердно работать;
3): ～な здоровый;
まめである, まめで暮らしている быть здоровым."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "まめ･忠実"
    assert first_res.reading == "まめ"
    assert first_res.mainsense == "～な честный, преданный"
    assert (
        first_res.senses
        == """1): ～な честный, преданный;
まめに勤める честно служить;
2): ～な старательный, усердный;
まめに働く усердно работать;
3): ～な здоровый;
まめである, まめで暮らしている быть здоровым."""
    )


def test_list_article_jun(parser):
    test_articles = [
        """じゅん　　　
純
1): ～な чистый, незапятнанный;
2): ～[な] чистый, беспримесный, без примеси."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "純"
    assert first_res.reading == "じゅん"
    assert first_res.mainsense == "～な чистый, незапятнанный"


def test_date_chouwa(parser):
    test_articles = [
        """ちょうわ　　
長和
1012.XII — 1017.IV"""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "長和"
    assert first_res.reading == "ちょうわ"
    assert first_res.mainsense == "1012.XII — 1017.IV"
    assert first_res.senses == "1012.XII — 1017.IV"


def test_recursive_articles(parser):
    test_articles = [
        """つく　　　　
木菟･木兎
см. <<みみずく>>.""",
        """かくしん　　
閣臣
уст. см. <<こくむだいじん>>.""",
    ]

    results = parser.process_results(test_articles)

    assert len(results) == 0


def test_colon_kaikan(parser):
    test_articles = [
        """かいかん　　
開罐･開缶
: ～する открывать банку (напр. консервов)."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "開罐･開缶"
    assert first_res.reading == "かいかん"
    assert first_res.mainsense == "～する открывать банку (напр. консервов)."


def test_colon_shoukei(parser):
    test_articles = [
        """しょうけい　
小慧
: ～の кн. толковый, смышлёный."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "小慧"
    assert first_res.reading == "しょうけい"
    assert first_res.mainsense == "～の кн. толковый, смышлёный."


def test_nonstandard_boudai(parser):
    test_articles = [
        """ぼうだい　　
厖大
неправ. 尨大
: ～な огромный, громадный;
厖大な本 объёмистая книга."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "厖大"
    assert first_res.reading == "ぼうだい"
    assert first_res.mainsense == "～な огромный, громадный"


def test_nonstandard_kakaru(parser):
    test_articles = [
        """かかる
как 2-ой компонент сложн. гл. указывает на начало и незаконченность действия:
начинается..., вот-вот..., почти..., чуть не..."""
    ]

    results = parser.process_results(test_articles)

    first_res = results[0]
    assert isinstance(first_res, Translation)
    assert first_res.word == "かかる"
    assert first_res.reading == "かかる"
    assert first_res.mainsense == "начинается..., вот-вот..., почти..., чуть не..."
