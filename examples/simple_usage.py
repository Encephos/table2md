from table2md.core import TableParser

# Liste von Testfällen mit verschiedenen HTML-Strukturen
test_tables = {
    # 1. Einfache Tabelle
    "Einfache Tabelle": """
        <table>
            <tr><th>Name</th><th>Alter</th></tr>
            <tr><td>Anna</td><td>30</td></tr>
            <tr><td>Bernd</td><td>25</td></tr>
        </table>
    """,

    # 2. Mit thead/tbody/tfoot
    "Mit thead/tbody/tfoot": """
        <table>
            <thead>
                <tr><th>Artikel</th><th>Preis</th></tr>
            </thead>
            <tbody>
                <tr><td>Apfel</td><td>1 €</td></tr>
                <tr><td>Banane</td><td>2 €</td></tr>
            </tbody>
            <tfoot>
                <tr><td>Summe</td><td>3 €</td></tr>
            </tfoot>
        </table>
    """,

    # 3. Mit caption
    "Mit caption": """
        <table>
            <caption>Verkaufsübersicht</caption>
            <tr><th>Monat</th><th>Umsatz</th></tr>
            <tr><td>Januar</td><td>1000 €</td></tr>
            <tr><td>Februar</td><td>1200 €</td></tr>
        </table>
    """,

    # 4. Mit style und border
    "Mit style/border": """
        <table style="border:2px solid black;">
            <tr><th>Spalte A</th><th>Spalte B</th></tr>
            <tr><td>Wert 1</td><td>Wert 2</td></tr>
        </table>
    """,

    # 5. Mit colgroup/col
    "Mit colgroup/col": """
        <table>
            <colgroup>
                <col span="2" style="background-color:lightblue">
                <col style="background-color:lightgreen">
            </colgroup>
            <tr><th>A</th><th>B</th><th>C</th></tr>
            <tr><td>1</td><td>2</td><td>3</td></tr>
        </table>
    """,

    # 6. Mit rowspan/colspan
    "Mit rowspan/colspan": """
        <table border="1">
            <tr>
                <th rowspan="2">Kategorie</th>
                <th colspan="2">Details</th>
            </tr>
            <tr>
                <th>Unterpunkt A</th>
                <th>Unterpunkt B</th>
            </tr>
            <tr>
                <td>Test</td>
                <td>Alpha</td>
                <td>Beta</td>
            </tr>
        </table>
    """,

    # 7. Mehrzeilige Header
    "Mehrzeilige Header": """
        <table>
            <thead>
                <tr><th colspan="2">Produkte</th></tr>
                <tr><th>Name</th><th>Preis</th></tr>
            </thead>
            <tbody>
                <tr><td>Apfel</td><td>1 €</td></tr>
                <tr><td>Banane</td><td>2 €</td></tr>
            </tbody>
        </table>
    """,

    # 8. Inline-Tags in Zellen
    "Inline-Tags in Zellen": """
        <table>
            <tr><th>Text</th></tr>
            <tr><td>Hier ein <b>fetter</b>, <i>kursiver</i> Text mit <a href='https://example.com'>Link</a></td></tr>
        </table>
    """,

    # 9. Leere Zellen / &nbsp;
    "Leere Zellen": """
        <table>
            <tr><th>Item</th><th>Value</th></tr>
            <tr><td>Test</td><td>&nbsp;</td></tr>
        </table>
    """,

    # 10. Verschachtelte Tabellen
    "Verschachtelte Tabellen": """
        <table>
            <tr>
                <td>
                    <table border="1">
                        <tr><th>Inner A</th><th>Inner B</th></tr>
                        <tr><td>1</td><td>2</td></tr>
                    </table>
                </td>
                <td>Außenwert</td>
            </tr>
        </table>
    """,

    # 11. Mit summary-Attribut
    "Mit summary": """
        <table summary="Beispielhafte Tabelle">
            <tr><th>Spalte 1</th><th>Spalte 2</th></tr>
            <tr><td>Wert A</td><td>Wert B</td></tr>
        </table>
    """,

    # 12. Mit footer Summenzeile
    "Mit footer Summenzeile": """
        <table>
            <thead>
                <tr><th>Monat</th><th>Umsatz</th></tr>
            </thead>
            <tbody>
                <tr><td>Januar</td><td>1000 €</td></tr>
                <tr><td>Februar</td><td>1200 €</td></tr>
            </tbody>
            <tfoot>
                <tr><td>Gesamt</td><td>2200 €</td></tr>
            </tfoot>
        </table>
    """,

    # 13. Verschachtelte Tabellen
    "Confluence Beispiel": """
        <div class="table-wrap">
            <table class="wrapped confluenceTable">
            <colgroup>
            <col>
            <col>
            </colgroup>
            <tbody>
            <tr>
                <td talk-marker="53" talk-page-id="454275164" talk-page-version="6" class="confluenceTd"><strong>Allgemein</strong></td>
                <td talk-marker="54" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="11">
                </td>
            </tr>
            <tr>
                <td talk-marker="55" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Applikation oder Solution-Name</td>
                <td talk-marker="56" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="12">
                </td>
            </tr>
            <tr>
                <td talk-marker="57" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Dateneigentümer Fachbereich</td>
                <td talk-marker="58" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="13">
                </td>
            </tr>
            <tr>
                <td talk-marker="59" talk-page-id="454275164" talk-page-version="6" class="confluenceTd"><strong>Vertraulichkeit</strong></td>
                <td talk-marker="60" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">(normal / erhöht)</td>
            </tr>
            <tr>
                <td talk-marker="61" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Welche Datenarten werden allgemein im System verarbeitet?</td>
                <td talk-marker="62" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="14">
                </td>
            </tr>
            <tr>
                <td talk-marker="63" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Welche personenbezogene Daten werden verarbeitet?
                <br talk-br="15">
                (inkl. Benutzerverwaltung - personalisierte Accounts)</td>
                <td talk-marker="64" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="16">
                </td>
            </tr>
            <tr>
                <td talk-marker="65" talk-page-id="454275164" talk-page-version="6" class="confluenceTd"><strong>Integrität</strong></td>
                <td talk-marker="66" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">(normal / erhöht)</td>
            </tr>
            <tr>
                <td talk-marker="67" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Verursacht eine Verletzung Rechtliche Konsequenzen?</td>
                <td talk-marker="68" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="17">
                </td>
            </tr>
            <tr>
                <td talk-marker="69" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Störung von Geschäftsprozessen?</td>
                <td talk-marker="70" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="18">
                </td>
            </tr>
            <tr>
                <td talk-marker="71" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Verursacht eine Verletzung Reputationsschäden?</td>
                <td talk-marker="72" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="19">
                </td>
            </tr>
            <tr>
                <td talk-marker="73" talk-page-id="454275164" talk-page-version="6" class="confluenceTd"><strong>Verfügbarkeit</strong></td>
                <td talk-marker="74" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">(normal / erhöht)</td>
            </tr>
            <tr>
                <td talk-marker="75" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Darf die IT-Solution/Applikation länger als 2-4h ausfallen?</td>
                <td talk-marker="76" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="20">
                </td>
            </tr>
            <tr>
                <td talk-marker="77" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Droht ein Werksstillstand bei Ausfall?</td>
                <td talk-marker="78" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="21">
                </td>
            </tr>
            <tr>
                <td talk-marker="79" talk-page-id="454275164" talk-page-version="6" class="confluenceTd"><strong>Sonstige</strong></td>
                <td talk-marker="80" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="22">
                </td>
            </tr>
            <tr>
                <td talk-marker="81" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Sind externe DLs beteiligt?</td>
                <td talk-marker="82" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="23">
                </td>
            </tr>
            <tr>
                <td talk-marker="83" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Wird ein Fernzugang für Support benötigt?</td>
                <td talk-marker="84" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="24">
                </td>
            </tr>
            <tr>
                <td talk-marker="85" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Wird das System extern gehostet (Cloud)?</td>
                <td talk-marker="86" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="25">
                </td>
            </tr>
            <tr>
                <td talk-marker="87" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">Soll das System direkt aus dem Internet erreichbar sein?
                <br talk-br="26">
                (DMZ-relevant, o. Ä.)</td>
                <td talk-marker="88" talk-page-id="454275164" talk-page-version="6" class="confluenceTd">
                <br talk-br="27">
                </td>
            </tr>
            </tbody>
            </table>
            </div>
    """
}


if __name__ == "__main__":
    # Durchlauf aller Testfälle
    for name, html in test_tables.items():
        print(f"\n=== Testfall: {name} ===")
        parser = TableParser(html)
        tables = parser.parse()

        for t in tables:
            print("Parsed object:", t)
            print(t.to_markdown())
