<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0">

    <!-- Version notes: this was changed by Hugh on 5.11.17 to serve the IGNTP Galatians transcriptions; it does not exploit the Firefox bug to display columns-->

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
                        <xsl:for-each select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt">
                            <xsl:choose>
                                <xsl:when test="@type=''">:</xsl:when>
                            </xsl:choose>
                            <xsl:value-of select="tei:title"/>
                        </xsl:for-each>
                    </h2>
                    <span class="title">
                        <strong>
                            <xsl:for-each select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier">
                                <strong>
                                    <xsl:value-of select="tei:msName"/>
                                </strong>
                                <xsl:choose>
                                    <xsl:when test="msName!=''">:</xsl:when>
                                </xsl:choose>
                                <xsl:value-of select="tei:settlement"/>
                                <xsl:choose>
                                    <xsl:when test="msName!=''">,</xsl:when>
                                </xsl:choose>
                                <xsl:value-of select="tei:repository"/>
                                <xsl:choose>
                                    <xsl:when test="msName!=''">:</xsl:when>
                                </xsl:choose>
                                <xsl:value-of select="tei:idno"/>
                            </xsl:for-each>
                        </strong>
                        <br/>
                    </span>
                    <span class="catalogues">
                        <xsl:for-each select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:altIdentifier">
                            <xsl:choose>
                                <xsl:when test="@type='partial'">
                                    <em>also</em>
                                    <xsl:apply-templates/>
                                    <br/>
                                </xsl:when>
                                <xsl:when test="@type='GA'">G–A <xsl:apply-templates/>
                                </xsl:when>
                                <xsl:when test="@type='Liste'"> (                                    <a target="_liste">
                                        <xsl:attribute name="href">http://intf.uni-muenster.de/vmr/NTVMR/ListeHandschriften.php?ObjID=<xsl:apply-templates/>
                                        </xsl:attribute>Liste</a>)
                                </xsl:when>
                                <xsl:when test="@type='Tischendorf'">; Tischendorf <xsl:apply-templates/>
                                </xsl:when>
                                <xsl:when test="@type='P.Oxy'">; P. Oxy <xsl:apply-templates/>
                                </xsl:when>
                                <xsl:when test="@type='LDAB'">; LDAB <xsl:apply-templates/>
                                </xsl:when>
                                <xsl:when test="@type='TM'">; TM <a target="_liste">
                                    <xsl:attribute name="href">http://www.trismegistos.org/ldab/text.php?tm=<xsl:apply-templates/>
                                    </xsl:attribute>
                                    <xsl:apply-templates/>
                                </a>
                            </xsl:when>
                        </xsl:choose>
                    </xsl:for-each>
                </span>
            </p>
            <p>
                <xsl:for-each select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt">
                    <xsl:value-of select="tei:resp"/>
                    <xsl:text></xsl:text>
                    <xsl:value-of select="tei:name"/>
                    <xsl:text></xsl:text>                    <!--xsl:value-of select="tei:note"/-->
                    <br/>
                </xsl:for-each>
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
<xsl:choose>
<xsl:when test="@n='0'"></xsl:when>
<xsl:otherwise>
    <p id="P-{@n}"/>
    <hr/>
    <p align="left">
        <xsl:choose>
            <xsl:when test="@type='page'">Page </xsl:when>
            <xsl:when test="@type='folio'">Folio </xsl:when>
            <xsl:otherwise>Page </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="@n[contains(.,'-')]">
                <xsl:value-of select="substring-after(substring-before(@n,'-'),'P')"/>
                <a href="#top">back to top</a>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@n"/>
                <a href="#top">back to top</a>
            </xsl:otherwise>
        </xsl:choose>
    </p>
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:otherwise>
</xsl:choose>
</xsl:template>
<xsl:template match="tei:cb">
<xsl:choose>
<xsl:when test="@n='1'"></xsl:when>
<xsl:when test="@n[contains(.,'C1-')]"></xsl:when>
<xsl:when test="@n[contains(.,'C2-')]">
    <p align="left">Column <xsl:value-of select="substring-after(substring-before(@n,'-'),'C')"/>
    </p>
</xsl:when>
<xsl:otherwise>
    <p align="left">Column <xsl:value-of select="@n"/>
    </p>
</xsl:otherwise>
</xsl:choose>
</xsl:template>
<xsl:template match="tei:lb">
<br/>
<span class="line_number">
<xsl:choose>
    <xsl:when test="@n='3'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='6'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='9'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='12'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='15'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='18'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='21'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='24'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='27'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='30'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='33'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='36'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='39'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='42'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='45'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='48'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='51'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='54'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='57'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:when test="@n='60'">
        <xsl:value-of select="@n"/>
    </xsl:when>
    <xsl:otherwise>
        <xsl:text></xsl:text>
    </xsl:otherwise>
</xsl:choose>
</span>
<xsl:choose>
<xsl:when test="@rend='hang'"></xsl:when>
<xsl:when test="@rend='rightJust'">
    <xsl:text></xsl:text>
</xsl:when>
<xsl:when test="@rend='centerJust'">
    <xsl:text></xsl:text>
</xsl:when>
<xsl:otherwise>
    <xsl:text></xsl:text>
</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- Text layout-->
<xsl:template match="tei:div[@type='chapter']">
<span class="verse_number" id="K-{@n}">
<strong>
    <xsl:value-of select="substring-after(@n,'K')"/>
:</strong>
</span>
<xsl:apply-templates/>
</xsl:template>
<xsl:template match="tei:ab">
<span class="verse_number" id="V-{@n}">
<strong>
    <xsl:value-of select="substring-after(@n,'V')"/>
</strong>
</span>
<xsl:apply-templates/>
</xsl:template>
<xsl:template match="tei:w">
<xsl:apply-templates/>
<xsl:text></xsl:text>
</xsl:template>
<xsl:template match="tei:pc">
<xsl:apply-templates/>
<xsl:text></xsl:text>
</xsl:template>
<xsl:template match="tei:div[@rend='rightJust']">
<p align="right">
<strong>
    <xsl:apply-templates/>
</strong>
</p>
</xsl:template>
<xsl:template match="tei:div[@rend='centerJust']">
<p align="center">
<strong>
    <xsl:apply-templates/>
</strong>
</p>
</xsl:template>
<xsl:template match="tei:div[@type='incipit']">
<span class="verse_number">
<strong>Inc.:</strong>
</span>
<xsl:apply-templates/>
</xsl:template>
<xsl:template match="tei:div[@type='explicit']">
<span class="verse_number">
<strong>Expl.:</strong>
</span>
<xsl:apply-templates/>
</xsl:template>

<!-- Notes-->
<xsl:template match="tei:note[@type='header']">
<!-- @Cat: this really needs to be on a line of its own at the top of each page -->
<span class="headernote">
<xsl:apply-templates/>
</span>
</xsl:template>
<xsl:template match="tei:note[@type='editorial']">
<span class="editorialnote">
<xsl:attribute name="title">
    <xsl:apply-templates/>
</xsl:attribute>
<sup> Note </sup>
</span>
</xsl:template>
<xsl:template match="tei:note[@type='transcriberQuery']">
</xsl:template>
<xsl:template match="tei:note[@type='local']">
<span class="localnote"><!--xsl:attribute name="title"><xsl:apply-templates/></xsl:attribute>
<sup> Note </sup--></span>
</xsl:template>
<xsl:template match="tei:note[@type='commentary']">
<span class="commentary">
<xsl:text>[Commentary]</xsl:text>
</span>
</xsl:template>

<!-- Gap, space, unclear-->
<xsl:template match="tei:gap">
<xsl:if test="@reason='lacuna/illegible'">
<span class="supplied" title="{@extent} {@unit} illegible/lacuna">[...]</span>
</xsl:if>
<xsl:if test="@reason='lacuna'">
<xsl:choose>
    <xsl:when test="@unit='verse'"></xsl:when>
    <xsl:otherwise>
        <span class="supplied" title="Lacuna of {@extent} {@unit}">[...]</span>
    </xsl:otherwise>
</xsl:choose>
</xsl:if>
<xsl:if test="@reason='illegible'">
<span class="supplied" title="{@extent} {@unit} illegible">[...]</span>
</xsl:if>
<xsl:if test="@reason='witnessEnd'">
<span class="supplied" title="End of witness">[– – –]</span>
</xsl:if>
</xsl:template>
<xsl:template match="tei:space">

</xsl:template>
<xsl:template match="tei:unclear">
<span class="unclear">
<xsl:apply-templates/>
</span>
</xsl:template>
<!-- @Cat: here is an underdot but we need them to appear under each character in the unclear tags><span class="unclear"><xsl:apply-templates/>̣</span-->

<!-- Corrections-->
<xsl:template match="tei:app">
	{<xsl:apply-templates/>
}
</xsl:template>

<xsl:template match="tei:rdg">
<span>
<xsl:attribute name="title">
    <xsl:choose>
        <xsl:when test="@type='orig'">First hand reading: <xsl:apply-templates/>
        </xsl:when>
        <xsl:when test="@type='corr'">
            <xsl:choose>
                <xsl:when test="@hand='firsthand'">Correction by first hand: <xsl:apply-templates/>
                </xsl:when>
                <xsl:when test="@hand='corrector'">Correction: <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>Corrector <xsl:value-of select="@hand"/>
:                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:when>
    <xsl:when test="@type='alt'">
        <xsl:choose>
            <xsl:when test="@hand='firsthand'">Alternative reading (first hand: <xsl:apply-templates/>
            </xsl:when>
            <xsl:otherwise>Alternative reading: <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:when>
</xsl:choose>
</xsl:attribute>
<xsl:choose>
<xsl:when test="@type='orig'">
    <span class="original">
        <xsl:choose>
            <xsl:when test="not(.//*)">[omission]</xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </span>
</xsl:when>
<xsl:when test="@type='alt'">/    <span class="original">
        <xsl:apply-templates/>
    </span>
</xsl:when>
<xsl:when test="@type='corr'">/    <span class="correction">
        <xsl:choose>
            <xsl:when test="not(.//*)">[deletion]</xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </span>
</xsl:when>
</xsl:choose>
</span>
</xsl:template>

<!-- Decorations and fw-->
<xsl:template match="tei:hi[@rend='overline']">
<span style="text-decoration:overline">
<xsl:apply-templates/>
</span>
<!-- @Cat: is there any way of turning the overline off and on again when there is a line break in the middle of the hi element? See, e.g. 09 P5vC1L6 to L7 -->
</xsl:template>
<xsl:template match="tei:fw">

<span>
<xsl:attribute name="title">
<xsl:value-of select="@type"/>
</xsl:attribute>
<xsl:apply-templates/>
</span>
</xsl:template>

<!-- margins-->
<xsl:template match="tei:seg[@subtype='pagetop']">
<xsl:apply-templates/>
<!-- @Cat: the following tr is another display fix for Firefox-->
<tr/>
</xsl:template>
<xsl:template match="tei:seg[@subtype='pagebottom']">
<td/>
<tr/>
<xsl:apply-templates/>
</xsl:template>

<!-- Supplied-->
<xsl:template match="tei:ex">(<xsl:apply-templates/>
)</xsl:template>

<xsl:template match="tei:supplied[@source='EditioPrinceps']">
<span class="editioprinceps">
<xsl:apply-templates/>
</span>
</xsl:template>
<xsl:template match="tei:supplied[not(@source='EditioPrinceps')]">
<span class="supplied">
<xsl:if test=" not((preceding::text()[ancestor::tei:w])[last()][ancestor::tei:supplied[not(@source='EditioPrinceps')]])
		or not(string(number(translate(child::text(), '- ', '')))='NaN')
		or not(string(number(translate(string(preceding::tei:w[1]//child::text()), '- ', '')))='NaN')
		or name((preceding::tei:gap|preceding::tei:w)[last()]) = 'gap'
		or (not(ancestor::tei:fw) and preceding::tei:w[1]/ancestor::tei:fw)
		or (not(ancestor::tei:rdg) and preceding::tei:w[1]/ancestor::tei:rdg)
		or (ancestor::tei:rdg and not(ancestor::tei:rdg = preceding::tei:w[1]/ancestor::tei:rdg))

	">[</xsl:if>
<xsl:apply-templates/>
<xsl:choose>
<xsl:when test=" not(following::text()[ancestor::tei:w][1][ancestor::tei:supplied[not(@source='EditioPrinceps')]])
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
<xsl:template match="tei:titleStmt">
</xsl:template>
<xsl:template match="tei:editionStmt">
</xsl:template>
<xsl:template match="tei:publicationStmt">
</xsl:template>
<xsl:template match="tei:country">
</xsl:template>
<xsl:template match="tei:msName">
</xsl:template>
<xsl:template match="tei:altIdentifier">
</xsl:template>
<xsl:template match="tei:encodingDesc">
</xsl:template>
<xsl:template match="tei:revisionDesc">
</xsl:template>
<xsl:template match="tei:sourceDesc">
</xsl:template>

</xsl:stylesheet>
