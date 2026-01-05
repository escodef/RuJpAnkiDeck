CARD_CSS = """
.card {
    font-family: "Segoe UI", "Helvetica", sans-serif;
    font-size: 22px;
    text-align: center;
    color: #e0e0e0;
    background-color: #2c2c2c;
}

.nightMode .card {
    background-color: #1a1a1a;
    color: #ffffff;
}

.jp { 
    font-size: 45px; 
    font-weight: bold; 
    color: #64b5f6; 
    margin-top: 10px;
}

.reading { 
    font-size: 22px; 
    color: #b0bec5; 
    margin-bottom: 10px; 
}

.meaning { 
    font-size: 28px; 
    font-weight: bold; 
    color: #81c784; 
}

.extra { 
    font-size: 18px; 
    color: #90a4ae; 
    font-style: italic; 
    margin-top: 15px; 
}

hr { 
    border: none; 
    border-top: 1px solid #444; 
    margin: 20px 0; 
}
"""

JP_RU_FRONT = '<div class="jp">{{Word}}</div>'
JP_RU_BACK = """{{FrontSide}}<hr>
<div class="reading">{{Reading}}</div>
<div class="meaning">{{MainSense}}</div>
<div class="extra">{{Senses}}</div>"""

RU_JP_FRONT = '<div class="meaning">{{MainSense}}</div>'
RU_JP_BACK = """{{FrontSide}}<hr>
<div class="jp">{{Word}}</div>
<div class="reading">{{Reading}}</div>
<div class="extra">{{Senses}}</div>"""
