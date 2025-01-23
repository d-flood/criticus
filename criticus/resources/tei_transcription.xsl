<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:tei="http://www.tei-c.org/ns/1.0">
    
    <!-- Version notes: This was changed by Hugh on 5.11.17 to serve the IGNTP Galatians transcriptions; it does not exploit the Firefox bug to display columns -->
    
    <xsl:template match="/">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                <title>IGNTP Transcription Display</title>
                
                <style type="text/css">
                    body { background-color:#fae6c3; font-family: Gentium, Times, Gentium Plus, Arial Unicode MS;}
                    div#header {}
                    h1 {font-family:Gentium, Times New Roman;
                    color:darkRed;
                    font-size:3em;
                    float:left;
                    display: inline;
                    }
                    h2 {
                    font-family:Gentium, Times New Roman;
                    font-size:1.5em;
                    }
                    a:link {
                    text-decoration:none;
                    }
                    a:visited {
                    text-decoration:none;
                    }
                    h3 {
                    font-family:Gentium, Times New Roman;
                    font-size:1.3em;
                    }
                    span#logo {font-family:Gentium, Times New Roman;
                    color:darkRed;
                    font-size:3em;
                    display: inline;
                    float:left;
                    }
                    span#top {font-family:Gentium, Times New Roman;
                    color:black;
                    font-size:1.5em;
                    display: inline;
                    float:bottom;
                    }
                    p.menu {clear: both;}
                    span.verse_number {color:grey;
                    font-size:0.8em;}
                    span.line_number {color:grey;
                    font-size:0.8em;}
                    span.catalogues {color:black;
                    font-size:1em;}
                    span.title {color:black;
                    font-size:1.3em;}
                    span.supplied{color:red;}
                    span.unclear{color:grey;}
                    span.editioprinceps{color:#44d8d1;}
                    span.correction{color:blue;}
                    span.original{color:green;}
                    span.editorialnote{color:blue;}
                    span.commentary{color:black;
                    font-style:italic;}
                    span.headernote{font-style:italic;}
                    span.localnote{color:white;}
                </style>
                
            </head>
            <body>
                <div id="header">
                    <a href="http://www.igntp.org/" target="_self">
                        <span id="logo">
                            <strong>igntp</strong>
                        </span>
                    </a>
                    <span id="top">
                        <strong>XML</strong>
                        <a href="https://github.com/d-flood/criticus">Criticus</a>
                    </span>
                </div>
                <div id="navigation">
                    <p>This stylesheet was created by the <a href="https://itseeweb.cal.bham.ac.uk/epistulae/">IGNTP and ITSEE and originally found on epistulae.org</a>
                    </p>
                    
                </div>
                
                <p>
                    <h2>
                        <xsl:apply-templates select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>
                    </h2>
                    <span class="title">
                        <strong>
                            <xsl:for-each select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier">
                                <xsl:value-of select="tei:msName, tei:settlement, tei:repository, tei:idno" separator=", "/>
                            </xsl:for-each>
                        </strong>
                        <br/>
                    </span>
                    <span class="catalogues">
                        <xsl:apply-templates select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:altIdentifier"/>
                    </span>
                </p>
                <p>
                    <xsl:apply-templates select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt"/>
                </p>
                
                <p>
                    <xsl:apply-templates/>
                    <hr/>
                </p>
            </body>
        </html>
    </xsl:template>
    
    <!-- Text stuff -->
    <!-- Page layout-->
    <xsl:template match="tei:pb">
        <xsl:if test="@n != '0'">
            <p id="P-{@n}"/>
            <hr/>
            <p align="left">
                <xsl:value-of select="if (@type='page') then 'Page' else if (@type='folio') then 'Folio' else 'Page'"/>
                <xsl:value-of select="if (contains(@n, '-')) then substring-after(substring-before(@n,'-'),'P') else @n"/>
                <a href="#top">back to top</a>
            </p>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="tei:cb">
        <xsl:choose>
            <xsl:when test="@n='1'"/>
            <xsl:when test="contains(@n,'C1-')"/>
            <xsl:when test="contains(@n,'C2-')">
                <p align="left">Column <xsl:value-of select="substring-after(substring-before(@n,'-'),'C')"/></p>
            </xsl:when>
            <xsl:otherwise>
                <p align="left">Column <xsl:value-of select="@n"/></p>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:lb">
        <br/>
        <span class="line_number">
            <xsl:value-of select="if (@n = ('3', '6', '9', '12', '15', '18', '21', '24', '27', '30', '33', '36', '39', '42', '45', '48', '51', '54', '57', '60')) then @n else ''"/>
        </span>
    </xsl:template>
    
    <!-- Text layout-->
    <xsl:template match="tei:div[@type='chapter']">
        <span class="verse_number" id="K-{@n}">
            <strong><xsl:value-of select="substring-after(@n,'K')"/>:</strong>
        </span>
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:ab">
        <span class="verse_number" id="V-{@n}">
            <strong><xsl:value-of select="substring-after(@n,'V')"/></strong>
        </span>
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:w">
        <xsl:apply-templates/>
        <xsl:if test="following-sibling::*[1][self::tei:w]"><xsl:text> </xsl:text></xsl:if>
        <xsl:text> </xsl:text>
    </xsl:template>
    
    <xsl:template match="tei:pc">
        <xsl:apply-templates/>
        <xsl:text></xsl:text>
        <xsl:text> </xsl:text>
    </xsl:template>
    
    <xsl:template match="tei:div[@rend='rightJust']">
        <p align="right">
            <strong><xsl:apply-templates/></strong>
        </p>
    </xsl:template>
    
    <xsl:template match="tei:div[@rend='centerJust']">
        <p align="center">
            <strong><xsl:apply-templates/></strong>
        </p>
    </xsl:template>
    
    <xsl:template match="tei:div[@type='incipit']">
        <span class="verse_number"><strong>Inc.:</strong></span>
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:div[@type='explicit']">
        <span class="verse_number"><strong>Expl.:</strong></span>
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- Notes-->
    <xsl:template match="tei:note[@type='header']">
        <span class="headernote"><xsl:apply-templates/></span>
    </xsl:template>
    
    <xsl:template match="tei:note[@type='editorial']">
        <span class="editorialnote" title="{.}">
            <sup> Note </sup>
        </span>
    </xsl:template>
    
    <xsl:template match="tei:note[@type='transcriberQuery']"/>
    
    <xsl:template match="tei:note[@type='local']">
        <span class="localnote"></span>
    </xsl:template>
    
    <xsl:template match="tei:note[@type='commentary']">
        <span class="commentary">[Commentary]</span>
    </xsl:template>
    
    <!-- Gap, space, unclear-->
    <xsl:template match="tei:gap">
        <xsl:choose>
            <xsl:when test="@reason='lacuna/illegible'">
                <span class="supplied" title="{@extent} {@unit} illegible/lacuna">[...]</span>
            </xsl:when>
            <xsl:when test="@reason='lacuna'">
                <span class="supplied" title="Lacuna of {@extent} {@unit}">[...]</span>
            </xsl:when>
            <xsl:when test="@reason='illegible'">
                <span class="supplied" title="{@extent} {@unit} illegible">[...]</span>
            </xsl:when>
            <xsl:when test="@reason='witnessEnd'">
                <span class="supplied" title="End of witness">[– – –]</span>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:space"/>
    
    <xsl:template match="tei:unclear">
        <span class="unclear"><xsl:apply-templates/></span>
    </xsl:template>
    
    <!-- Corrections-->
    <xsl:template match="tei:app">
        {<xsl:apply-templates/>}
    </xsl:template>
    
    <xsl:template match="tei:rdg">
        <span title="{
            if (@type='orig') then 'First hand reading: ' else if (@type='corr') then (
                    if (@hand='firsthand') then 'Correction by first hand: ' else if (@hand='corrector') then 'Correction: ' else 'Corrector ' || @hand || ': '
                ) else if (@type='alt') then (
                    if (@hand='firsthand') then 'Alternative reading (first hand: ' else 'Alternative reading: '
                ) else ''
                     }"><xsl:apply-templates/></span>
        <xsl:choose>
            <xsl:when test="@type='orig'">
                <span class="original">
                    <xsl:choose>
                        <xsl:when test="not(.//*)">[omission]</xsl:when>
                        <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
                    </xsl:choose>
                </span>
            </xsl:when>
            <xsl:when test="@type='alt'">/ <span class="original"><xsl:apply-templates/></span></xsl:when>
            <xsl:when test="@type='corr'">/ <span class="correction">
                    <xsl:choose>
                        <xsl:when test="not(.//*)">[deletion]</xsl:when>
                        <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
                    </xsl:choose>
                </span></xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <!-- Decorations and fw-->
    <xsl:template match="tei:hi[@rend='overline']">
        <span style="text-decoration:overline"><xsl:apply-templates/></span>
    </xsl:template>
    
    <xsl:template match="tei:fw">
        <span title="{@type}"><xsl:apply-templates/></span>
    </xsl:template>
    
    <!-- margins-->
    <xsl:template match="tei:seg[@subtype='pagetop']">
        <xsl:apply-templates/>
        <tr/>
    </xsl:template>
    
    <xsl:template match="tei:seg[@subtype='pagebottom']">
        <td/>
        <tr/>
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- Supplied-->
    <xsl:template match="tei:ex">(<xsl:apply-templates/>)</xsl:template>
    
    <xsl:template match="tei:supplied[@source='EditioPrinceps']">
        <span class="editioprinceps"><xsl:apply-templates/></span>
    </xsl:template>
    
    <xsl:template match="tei:supplied[not(@source='EditioPrinceps')]">
        <span class="supplied">
            <xsl:if test="
                not((preceding::text()[ancestor::tei:w])[last()][ancestor::tei:supplied[not(@source='EditioPrinceps')]])
                or not(string(number(translate(child::text(), '- ', '')))='NaN')
                or not(string(number(translate(string(preceding::tei:w[1]//child::text()), '- ', '')))='NaN')
                or name((preceding::tei:gap|preceding::tei:w)[last()]) = 'gap'
                or (not(ancestor::tei:fw) and preceding::tei:w[1]/ancestor::tei:fw)
                or (not(ancestor::tei:rdg) and preceding::tei:w[1]/ancestor::tei:rdg)
                or (ancestor::tei:rdg and not(ancestor::tei:rdg = preceding::tei:w[1]/ancestor::tei:rdg))
                        ">[</xsl:if>
            <xsl:apply-templates/>
            <xsl:choose>
                <xsl:when test="
                    not(following::text()[ancestor::tei:w][1][ancestor::tei:supplied[not(@source='EditioPrinceps')]])
                    or not(string(number(translate(child::text(), '- ', '')))='NaN')
                    or not(string(number(translate(string(following::tei:w[1]//child::text()), '- ', '')))='NaN')
                    or name((following::tei:gap|following::tei:w)[1]) = 'gap'
                    or (ancestor::tei:fw and not(following::tei:w[1]/ancestor::fw))
                    or (not(ancestor::tei:rdg) and following::tei:w[1]/ancestor::tei:rdg)
                    or (ancestor::tei:rdg and not(ancestor::tei:rdg = following::tei:w[1]/ancestor::tei:rdg))
                            ">]</xsl:when>
                <xsl:otherwise></xsl:otherwise>
            </xsl:choose>
        </span>
    </xsl:template>
    
    <!-- header stuff -->
    <xsl:template match="tei:titleStmt"/>
    <xsl:template match="tei:editionStmt"/>
    <xsl:template match="tei:publicationStmt"/>
    <xsl:template match="tei:country"/>
    <xsl:template match="tei:msName"/>
    <xsl:template match="tei:altIdentifier"/>
    <xsl:template match="tei:encodingDesc"/>
    <xsl:template match="tei:revisionDesc"/>
    <xsl:template match="tei:sourceDesc"/>
    
</xsl:stylesheet>