"""Euskara."""

TEXTOS = {
    "nav.cerca": "Gertu", "nav.mapa": "Mapa", "nav.tendencia": "Joera", "nav.ajustes": "Ezarpenak",
    "aria.combustible": "Erregaia", "aria.secciones": "Atalak",
    "comb.g95": "Gasolina 95", "comb.g98": "Gasolina 98", "comb.diesel": "Diesela",
    "comb.diesel_plus": "Diesel+", "comb.glp": "GLP", "comb.gnc": "GNC", "comb.gnl": "GNL",

    "inicio.primera_vez": "Hasteko, esan iezaguzu non bilatu gasolindegiak: etxean, lanean edo orain zauden "
                          "tokian. Espainia osoan balio du.",
    "inicio.ir_ajustes": "Kokapena aukeratu",
    "inicio.sin_precios": "Oraindik ez dago {comb} preziorik {radio} km baino gertuago.",
    "inicio.sin_precios_nota": "Saiatu erradioa handitzen Ezarpenetan.",
    "inicio.mas_barata": "Merkeena, {radio} km baino gertuago",
    "inicio.ahorro": "Hemen {litros} {unidad} hartzeak <b>{coste}</b> balio du: <b>{ahorro}</b> aurrezten duzu "
                     "inguruko batez bestekoaren aldean ({media}).",
    "inicio.resto": "Gertuko besteak",
    "inicio.mas_cercana": "Hurbilena", "inicio.ordenar": "Zerrenda ordenatu",
    "orden.precio": "Merkeenak", "orden.distancia": "Hurbilenak",
    "inicio.resto_nota": "{total} guztira · zentimoak batez bestekoaren aldean",
    "como_llegar": "Nola iritsi", "historial": "Historia",
    "actualizar_ahora": "Prezioak orain eguneratu",
    "pie.datos": "Ministerioaren prezioak · {fecha}(e)ko datuak",
    "pie.sin_leer": "Ministerioaren prezioak · oraindik irakurri gabe",

    "mapa.titulo": "Mapa", "mapa.aria": "Gasolindegien mapa",
    "filtro.aria": "Mapa iragazi",
    "filtro.abiertas": "Orain irekita",
    "filtro.baratas": "Merkeagoak", "filtro.baratas_ayuda": "Batez bestekoa baino merkeagoak",
    "filtro.marcas": "Markak",
    "filtro.marcas_titulo": "Zein marka ikusi nahi dituzu?",
    "filtro.todas": "Denak",
    "filtro.ninguna": "Bat ere ez",
    "filtro.listo": "Eginda",
    "js.filtro_cuenta": "{total} gasolindegitik {n}.",
    "mapa.leyenda": '<span class="barata" aria-hidden="true">●</span> merkeena · <span class="cara" aria-hidden="true">●</span> garestiena, '
                    "zure erradiokoekin alderatuta. Ukitu bat haren ordutegia eta nola iritsi ikusteko.",

    "estacion.de_casa": "zure kokapenetik {distancia}(e)ra",
    "estacion.ultimos": "{comb}, azken 90 egunak",
    "estacion.sin_historico": "Oraindik ez dago historiarik: aplikazioak prezio bat gordetzen du egunean, eta "
                              "grafikoa bi daudenean agertzen da.",
    "estacion.no_existe": "Gasolindegi hori ez dago datu-basean.",
    "estacion.coste": "Hemen {litros} {unidad} {comb} hartzea: <b>{coste}</b>",
    "serie.esta": "Gasolindegi hau", "serie.zona": "Inguruko batez bestekoa", "serie.media": "Batez bestekoa",
    "serie.minimo": "Merkeena", "serie.brent": "Brent (€/upela)",

    "tend.sin_datos": "Oraindik ez dago {comb} daturik zure inguruan.",
    "tend.media_hoy": "Batez bestekoa gaur", "tend.vs7": "Duela 7 egun", "tend.vs30": "Duela 30 egun",
    "tend.cts": "zt",
    "tend.zona": "{comb}, {radio} km baino gertuago",
    "tend.grafica_pronto": "Grafikoa bi egunetako datuak daudenean agertzen da. Aplikazioak prezio bat gordetzen "
                           "du egunean.",
    "tend.dia_titulo": "Zein egunetan da merkeagoa?",
    "tend.dia_mejor": "Batez beste, <b>{dia}</b> da zure inguruan erregaia hartzeko egunik merkeena.",
    "tend.brent_retraso": "Brent-a {fecha} arte dago: EIAk astean behin argitaratzen du, egun batzuetako "
                          "atzerapenarekin. Iragarpenak kontuan hartzen du hori.",
    "js.brent_pendiente": "oraindik argitaratu gabe",
    "tend.dia_faltan": "Gutxienez bi asteko datuak behar dira jakiteko. {dias} egun daramatzazu.",
    "marcas.titulo": "Markak zure inguruan",
    "marcas.nota": "Marka bakoitza inguruko batez bestekoa baino zenbat merkeago edo garestiago dagoen, azken "
                   "{dias} egunetan eta {radio} km baino gutxiagora. Gutxienez bi gasolindegi dituzten markak "
                   "bakarrik.",
    "marcas.gasolineras": "{n} gasolindegi",
    "rep.titulo": "Nire hornitzeak",
    "rep.aqui": "Hornitzea apuntatu",
    "rep.este_mes": "Hilabete honetan",
    "rep.doce_meses": "Azken 12 hilabeteak",
    "rep.consumo": "Kontsumoa ({unidad}/100 km)",
    "rep.consumo_falta": "Zure benetako kontsumoa jakiteko, apuntatu kilometro-kontagailuaren km-ak depositua "
                         "beteta duten bi hornitzetan.",
    "rep.usar_consumo": "Nire benetako kontsumoa Ezarpenetan erabili",
    "rep.consumo_valor": "{consumo} {unidad}/100 km",
    "rep.apuntar": "Hornitze bat apuntatu",
    "rep.fecha": "Data",
    "rep.litros": "Kopurua ({unidad})",
    "rep.precio": "Prezioa (€/{unidad})",
    "rep.km": "Kilometro-kontagailua (km, aukerakoa)",
    "rep.lleno": "Depositua bete dut",
    "rep.guardar": "Hornitzea gorde",
    "rep.privado": "Nabigatzaile honetan bakarrik gordetzen da: Pumpcast-ek ez du ikusten. Mugikorra aldatzen "
                   "baduzu edo nabigatzailearen datuak ezabatzen badituzu, galdu egiten da; esportatu kopia "
                   "bat noizean behin.",
    "rep.historial": "Historia",
    "rep.vacio": "Oraindik ez duzu hornitzerik apuntatu.",
    "rep.exportar": "Kopia esportatu",
    "rep.importar": "Kopia inportatu",
    "rep.error": "Begiratu kopurua eta prezioa (eta km-ak, jarri badituzu).",
    "rep.borrar": "Ezabatu",
    "rep.borrar_seguro": "Hornitze hau ezabatu?",
    "rep.importados": "{n} hornitze inportatu dira.",
    "rep.importar_mal": "Fitxategi hori ez da Pumpcast-en kopia bat.",
    "rep.lleno_corto": "beteta",
    "rep.km_corto": "{km} km",
    "voz.titulo": "Siri edo laguntzailearekin",
    "voz.intro": "Eskatu gasolindegia mugikorra ukitu gabe: esan <b>«Oye Siri, gasolinera barata»</b> eta "
                 "mapen aplikazioa irekiko da inguruko merkeenera, orain irekita badago. Autorako pentsatua.",
    "voz.ajustes": "Zure Ezarpenetako erradioan ({radio} km) eta zure erregaiarekin ({comb}) bilatzen du.",
    "voz.iphone": "iPhone eta CarPlay: Sirirekin",
    "voz.instalar": "Lasterbidea instalatu",
    "voz.atajo_viene": "{comb} eta {app}-erako prestatuta dator.",
    "voz.atajo_cambiar": "Zure kasurako, instalatu ondoren editatu lasterbidearen helbidea eta aldatu "
                         "<code>{de}</code> <code>{a}</code>-gatik.",
    "voz.o_crealo": "Edo sortu zuk zeuk minutu pare batean:",
    "voz.paso1": "Ireki <b>Atajos</b> aplikazioa eta sakatu <b>+</b> berri bat sortzeko.",
    "voz.paso2": "Gehitu <b>Obtener ubicación actual</b>.",
    "voz.b2": "Gehitu <b>Obtener contenido de URL</b> eta itsatsi helbide hau (sakatu kopiatzeko):",
    "voz.b2_nota": "Aldatu LAT zure kokapenagatik: ezabatu, sakatu «Ubicación actual» teklatuaren gainean, "
                   "sakatu aldagai hori eta aukeratu <b>Latitud</b>. Berdin LON eta <b>Longitud</b>-ekin.",
    "voz.b3": "Gehitu <b>Abrir URL</b>: aurreko urratsak itzulitakoa irekiko du, hau da, ibilbidea zure "
              "mapa-aplikazioan.",
    "voz.permiso": "Apple Maps-ek ibilbidea erakusten du eta «Ir» sakatu behar da; Google Maps eta Waze berez "
                   "abiatzen dira. Mugikorra blokeatuta badago, iOSek desblokeatzeko eska diezazuke.",
    "voz.simple_titulo": "Ekintza bakarreko bertsioa",
    "voz.simple": "Sortzeko errazagoa: <b>Abrir URL</b> bakarrik, helbide honekin. Baina Safari irekitzen da, "
                  "kokapena eskatzen dizu (Ajustes › Apps › Safari › Ubicación › Permitir, gehiago galde ez "
                  "dezan) eta, mapa ireki aurretik, iOSek galdetzen du «¿Abrir esta página en…?»: «Abrir» "
                  "sakatu behar da.",
    "voz.paso3": "Jarri <b>Gasolinera barata</b> izena (edo esan nahi duzuna) eta gorde. Kitto: «Oye Siri, "
                 "gasolinera barata».",
    "voz.otros": "Beste mapa-aplikazio baterako, gehitu amaieran <code>&amp;mapa=google</code>, "
                 "<code>&amp;mapa=waze</code> edo <code>&amp;mapa=apple</code>. Merkeenaren ordez hurbilena "
                 "nahi baduzu, <code>&amp;orden=distancia</code>; bidaia kontuan hartuta gehien merezi duena, "
                 "<code>&amp;orden=compensa</code>.",
    "voz.avanzado_titulo": "Siriak prezioa ozen esan dezan",
    "voz.avanzado": "Ekintza gehiago batzuekin, Siriak erantzuten du («La más barata a menos de 10 km es "
                    "Ballenoil, a 1,4 km: 1,729 euros el litro») eta gero mapa irekitzen du. Horrela ez da "
                    "Safariren baimenik behar:",
    "voz.a1": "Gehitu <b>Obtener ubicación actual</b>.",
    "voz.a2": "Gehitu <b>Obtener contenido de URL</b> helbide honekin, LAT eta LON kokapenaren <b>Latitud</b> "
              "eta <b>Longitud</b> aldagaiekin ordezkatuta:",
    "voz.a3": "Gehitu <b>Obtener valor de diccionario</b> (bilatu «diccionario») <b>frase</b> gakoarekin eta, "
              "ondoren, testu bat ozen irakurtzen duen ekintza (bilatu «texto»).",
    "voz.a4": "Gehitu berriro <b>Obtener valor de diccionario</b>, <b>apple</b> gakoarekin (edo "
              "<b>google</b>, <b>waze</b>) eta, hiztegi gisa, <b>Contenido de la URL</b>. Amaitu <b>Abrir "
              "URL</b> ekintzarekin.",
    "voz.android": "Android: ukitu batera",
    "voz.android_texto": "Googlek ez du uzten web batek ahots-aginduak gehitzea bere laguntzaileari. "
                         "Erosoena: instalatu Pumpcast hasierako pantailan, eduki sakatuta bere ikonoa eta "
                         "aukeratu <b>Merkeena gertu</b>; sarbide hori pantailara arrastatu dezakezu ukitu "
                         "batera izateko. Google Maps irekitzen du, dagoeneko hara nabigatzen.",
    "voz.probar": "Probatu orain",
    "voz.atajo": "Merkeena gertu",
    "voz.buscando": "Non zauden bilatzen…",
    "voz.abrir_app": "Ireki Pumpcast",
    "pasar.titulo": "Beste mugikor batera pasatu",
    "pasar.intro": "Eraman zure ezarpenak, gogokoak eta hornitzeak beste mugikor edo nabigatzaile batera, "
                   "konturik gabe: eskaneatu kodea beste mugikorraren kamerarekin edo bidali zeure buruari "
                   "esteka.",
    "pasar.lleva": "Hau darama: {que}.",
    "pasar.ajustes": "zure ezarpenak eta kokapena",
    "pasar.favoritas": "{n} gogoko",
    "pasar.repostajes": "{n} hornitze",
    "pasar.y": "eta ",
    "pasar.nada": "Oraindik ez dago ezer pasatzeko: aukeratu zure kokapena Ezarpenetan.",
    "pasar.qr_aria": "Zure datuak pasatzeko esteka duen QR kodea",
    "pasar.grande": "Datu gehiegi dago QR kode baterako: erabili esteka.",
    "pasar.compartir": "Esteka partekatu",
    "pasar.copiar": "Esteka kopiatu",
    "pasar.privado": "Dena estekaren barruan doa, «#» ikurraren ondoren: zati hori ez da inoiz zerbitzarira "
                     "iristen. Esteka duenak zure kokapena ikusten du; beraz, bidali zeure buruari bakarrik.",
    "pasar.importar_titulo": "Beste mugikor batetik ekarri",
    "pasar.importar_intro": "Esteka honek dakar:",
    "pasar.importar_aviso": "Mugikor honetako ezarpenak eta gogokoak ordezkatzen ditu; hornitzeak lehendik "
                            "daudenei gehitzen zaizkie.",
    "pasar.importar_boton": "Mugikor honetan inportatu",
    "pasar.importado": "Eginda: dena duzu mugikor honetan.",
    "pasar.importar_mal": "Esteka hau osatu gabe dago edo ez da Pumpcast-ena.",
    "pasar.ir_inicio": "Joan Pumpcast-era",
    "voz.precio": "{radio} km baino gutxiagora merkeena {nombre} da, {municipio}n, {distancia}ra: {precio} "
                  "euro {unidad}ko.",
    "voz.distancia": "Hurbilena {nombre} da, {municipio}n, {distancia}ra: {precio} euro {unidad}ko.",
    "voz.compensa": "{radio} km baino gutxiagora gehien merezi duena {nombre} da, {municipio}n, "
                    "{distancia}ra: {precio} euro {unidad}ko.",
    "voz.nada": "Ez dut preziodun gasolindegirik aurkitzen {radio} km baino gutxiagora.",
    "voz.fuera": "Kokapen hori Espainiatik kanpo dago, eta Pumpcast-ek Espainiako gasolindegiak bakarrik "
                 "ditu.",
    "voz.unidad_l": "litro",
    "voz.unidad_kg": "kilo",
    "voz.hor_24h": "24 orduz irekita dago.",
    "voz.hor_cierra": "{hora}etan ixten da.",
    "voz.hor_abre": "Orain itxita dago; {hora}etan irekitzen da.",
    "voz.hor_cerrada": "Orain itxita dago.",

    "prev.titulo": "Gaur bete ala itxaron?",
    "prev.provincia": "{provincia} probintzia osoko prezioekin kalkulatua.",
    "prev.nombre_gasoil": "Handizkako gasolioa", "prev.nombre_gasolina": "Handizkako gasolina",
    "prev.semana_hasta": "{fecha} arteko astea",
    "prev.acierta": "% {pct}etan asmatzen du; beti «Berdin dio» esanda, % {base}etan.",
    "prev.detalles": "Nola kalkulatzen da?",
    "prev.como": "Iragarpenak begiratzen du zenbat igo edo jaitsi den handizkako erregaia (Brent-a, "
                 "gasentzat) argitaratutako azken astean, eta zenbat mugitu den zure probintziako prezioa: "
                 "hornigailua merkatuaren atzetik doa, jaitsi baino azkarrago igotzen da eta prezioek "
                 "inertzia dute.",
    "prev.prueba": "Azken 60 egunekin probatua, horietatik ikasi gabe: <b>{total}etik {aciertos}</b> aldiz "
                   "asmatuko zukeen (% {pct}), batez beste {error} zentimoko errorearekin.",
    "prev.seguimiento": "Apuntatzen hasi zenetik: <b>{total}etik {aciertos}</b> asmatu.",
    "prev.apuntando": "Iragarpen bakoitza apuntatzen da; aste batean ikusten hasiko da benetan asmatzen duen.",
    "prev.aviso": "Pista bat da, ez berme bat: ez ditu aurreikusten gerrak, zergak edo zubiak bezalako ustekabeak.",
    "prev.cargando": "Ministerioaren eta petrolioaren prezioen historia kargatzen. 100 bat egunetako datuak "
                     "behar dira: {dias} dituzu. Lehen aldian ordu batzuk behar ditu.",
    "sem.llena": "Bete orain", "sem.igual": "Berdin dio", "sem.espera": "Itxaron ahal baduzu",
    "frase.llena": "Aste honetan {cts} zentimo inguru igotzea espero da ({euros} gehiago depositu bakoitzeko "
                   "itxaroten baduzu).",
    "frase.espera": "Aste honetan {cts} zentimo inguru jaistea espero da ({euros} gutxiago depositu bakoitzeko "
                    "itxaroten baduzu).",
    "frase.igual": "Ez da aldaketa handirik espero aste honetan.",

    "dia.0": "Astelehena", "dia.1": "Asteartea", "dia.2": "Asteazkena", "dia.3": "Osteguna", "dia.4": "Ostirala",
    "dia.5": "Larunbata", "dia.6": "Igandea",
    "dia_frase.0": "astelehena", "dia_frase.1": "asteartea", "dia_frase.2": "asteazkena", "dia_frase.3": "osteguna",
    "dia_frase.4": "ostirala", "dia_frase.5": "larunbata", "dia_frase.6": "igandea",

    "aj.titulo": "Ezarpenak", "aj.guardado": "Gordeta.", "aj.guardar": "Gorde",
    "aj.prueba_ok": "Proba-mezua bidali da. Begiratu Telegram.",
    "aj.prueba_error": "Ezin izan da bidali. Berrikusi TELEGRAM_TOKEN eta TELEGRAM_CHAT.",
    "aj.casa": "Kokapena", "aj.buscar_ph": "Kalea, zenbakia eta herria", "aj.buscar": "Bilatu",
    "aj.buscar_aria": "Helbidea bilatu", "aj.mapa_aria": "Kokapena aukeratzeko mapa",
    "aj.privacidad": "Zure kokapena eta hobespenak nabigatzaile honetan bakarrik gordetzen dira (cookie bat). "
                     "Zerbitzariak orria prestatzeko erabiltzen ditu, eta ez ditu inon apuntatzen.",
    "aj.olvidar": "Nire kokapena ahaztu",
    "aj.mapa_ayuda": "Bilatu zure helbidea, ukitu mapa edo arrastatu orratza. Gero, Gorde.",
    "aj.mi_ubicacion": "Nire kokapena erabili", "aj.coordenadas": "Koordenatuak eskuz",
    "aj.gps": "Aplikazioa irekitzen dudan bakoitzean nagoen tokia erabili",
    "aj.gps_nota": "Irekitzean, mugikorrak non zauden esaten du (100 m ingurura biribilduta) eta han bilatzen du. "
                   "Ezin badu, goiko kokapena erabiltzen du.",
    "aj.latitud": "Latitudea", "aj.longitud": "Longitudea", "aj.radio": "Erradioa (km)",
    "aj.coche": "Autoa", "aj.combustible": "Erregaia",
    "aj.litros": "Zenbat hartu ohi duzun (litroak; kiloak gas naturala bada)",
    "mapas.titulo": "Zein aplikaziorekin joan nahi duzu?", "mapas.cancelar": "Utzi",
    "js.como_llegar": "Nola iritsi",
    "aj.avisos": "Telegram bidezko abisuak",
    "aj.telegram_falta": "Telegram ez dago konfiguratuta: gehitu TELEGRAM_TOKEN eta TELEGRAM_CHAT edukiontziari.",
    "aj.resumen": "Laburpena goizero", "aj.hora": "Laburpenaren ordua",
    "aj.chollos": "Eskaintzen berri eman (8etatik 22etara)",
    "aj.umbral": "Eskaintza = 30 eguneko batez bestekoaren azpitik (€/L)",
    "aj.idioma": "Hizkuntza", "aj.idioma_auto": "Nabigatzailearena",
    "aj.enviar_prueba": "Proba-mezu bat bidali",
    "aj.version": "{version} bertsioa", "aj.ultima": "azken irakurketa {fecha}",

    "err.ubicacion": "Kokapena ez da baliozkoa.",
    "err.fuera": "Pumpcast-ek Espainiako prezioak bakarrik ditu: aukeratu barruko toki bat.",
    "err.radio": "Erradioak 1 eta 50 km artean egon behar du.",
    "err.litros": "Aldi bakoitzean hartzen duzunak 1 eta 150 artean egon behar du.",
    "err.umbral": "Eskaintzaren muga euro litroko doa, adibidez 0,05.",
    "err.numero": "Zenbakiren bat gaizki idatzita dago.",
    "err.hora": "Abisuaren ordua 08:30 bezala idatzi behar da.",
    "err.combustible": "Erregai hori ez dago.",
    "err.idioma": "Hizkuntza hori ez dago erabilgarri.",

    "js.casa": "Zure kokapena", "js.ver_historial": "Historia ikusi",
    "js.buscando": "Bilatzen…", "js.escribe_mas": "Idatzi helbidearen zati gehiago.",
    "js.no_encontrada": "Ez dut helbide hori aurkitu. Saiatu kalearekin eta herriarekin.",
    "js.elige": "Aukeratu ona:",
    "js.encontrada": "Helbidea aurkitu da. Zure atari zehatza ez bada, arrastatu orratza.",
    "js.no_se_pudo_buscar": "Ezin izan da bilatu: ", "js.movida": "Orratza mugituta.",
    "js.tocado": "Kokapena ukitu duzun tokian jarrita.", "js.coordenadas": "Koordenatuak jarrita.",
    "js.sin_gps": "Nabigatzaile honek ez du kokapena ematen.", "js.buscando_gps": "Non zauden bilatzen…",
    "js.gps_ok": "Zure oraingo kokapena jarrita.", "js.no_se_pudo": "Ezin izan da: ",
    "js.guardar": " Orain sakatu Gorde.",
    "js.fuente_busqueda": "(Bilaketa: © OpenStreetMap, Nominatim)",
    "pie.fuente": "Prezioak: Trantsizio Ekologikorako eta Erronka Demografikorako Ministerioa",
    "legal.en_castellano": "Lege-oharra gaztelaniaz dago, hori baita balio duen testua.",
    "pie.actualizado": "eguneratuta {fecha}", "pie.legal": "Lege-oharra eta pribatutasuna",
    "e404.titulo": "Orri hau ez dago",
    "e404.texto": "Baliteke esteka gaizki idatzita egotea edo orria jada ez egotea.",
    "e404.volver": "Hasierara joan",
    "js.gps_movido": "Mugitu egin zara: hemen gasolindegiak bilatzen…",
    "js.gps_ultima": "Ez dakit orain non zauden: zure azken kokapena erabiltzen dut.",
    "js.gps_fuera": "Orain Espainiatik kanpo zaude: zure azken kokapena erabiltzen dut.",
    "js.falta_ubicacion": "Lehenik aukeratu non: bilatu helbide bat, ukitu mapa edo erabili zure kokapena.",

    "off.titulo": "Konexiorik gabe",
    "off.texto": "Ez dago konexiorik eta pantaila hau ez zegoen gordeta. Ireki behin konexioarekin "
                 "eta erabilgarri geratuko da.",
    "off.aviso": "Konexiorik gabe · {fecha}(e)ko datuak",
    "manifest.descripcion": "Zure inguruko gasolindegi merkeenak, eta gaur betetzea merezi duen.",
    "api.sin_ubicacion": "Kokapena falta da: gehitu ?lat=...&lon=... URLari edo aukeratu Ezarpenetan.",

    "admin.titulo": "Administrazioa", "admin.entrar": "Sartu", "admin.salir": "Irten",
    "admin.clave": "Pasahitza", "admin.codigo": "Zure autentifikazio-aplikazioaren 6 zifrako kodea",
    "admin.error": "Pasahitza edo kodea okerra.",
    "admin.bloqueado": "Huts egindako saiakera gehiegi. Itxaron ordu-laurden bat.",
    "admin.alta_titulo": "Bi urratseko egiaztapena",
    "admin.alta_texto": "Panela babesten amaitzeko, gehitu zure autentifikazio-aplikazioan (Google "
                        "Authenticator, Aegis, 1Password...): eskaneatu kodea, edo sakatu botoia mugikorrean "
                        "bazaude. Gero idatzi ematen dizun 6 zifrako kodea.",
    "admin.alta_qr": "Autentifikazio-aplikaziorako QR kodea",
    "admin.alta_enlace": "Autentifikazio-aplikazioan ireki",
    "admin.alta_clave": "Edo idatzi gako hau eskuz aplikazioan:",
    "admin.confirmar": "Berretsi eta sartu",
    "admin.codigo_mal": "Kode horrek ez du balio. Egiaztatu mugikorraren ordua ondo dagoela eta saiatu "
                        "hurrengoarekin.",
    "admin.ubicacion": "Abisuen kokapena",
    "admin.ubicacion_nota": "Zure Telegram abisuetarako bakarrik. Ez da webgunean erakusten.",
    "admin.idioma_avisos": "Abisuen hizkuntza",
    "admin.lectura_ok": "Prezioak eguneratuta.",
    "admin.lectura_error": "Ezin izan dira Ministerioaren prezioak irakurri. Berriro saiatuko da bere kabuz.",

    "tg.hoy": "⛽ <b>{comb} gaur</b>, {radio} km baino gertuago",
    "tg.media": "Inguruko batez bestekoa: {media}. Lehenengoan {litros} {unidad} hartzeak <b>{coste}</b> "
                "balio du eta <b>{ahorro}</b> aurrezten duzu.",
    "tg.sube": "{cts} zentimo igo da duela aste batetik.",
    "tg.baja": "{cts} zentimo jaitsi da duela aste batetik.",
    "tg.igual": "Duela aste bat bezala.",
    "tg.chollo": "🔥 <b>Eskaintza</b>: {comb} <b>{precio}</b>, {sitio}.\n"
                 "Azken 30 egunetako batez bestekoa ({media}) baino {cts} zentimo gutxiago.",
    "tg.prueba": "✅ Pumpcast-en proba: abisuak ondo iristen dira.",
    "inicio.mas_barata_abierta": "Irekita dagoen merkeena, {radio} km baino gertuago",
    "inicio.favoritas": "Zure gogokoak",
    "orden.compensa": "Errentagarrienak",
    "inicio.con_viaje": "{coste} bidaiarekin",
    "inicio.compensa_nota": "Eskuinean, {litros} {unidad}(e)gatik ordaintzen duzuna gehi joan-etorriko erregaia, {consumo} {unidad}/100 km-ko kontsumoarekin. Aldatu Ezarpenetan.",
    "hor.24h": "Irekita 24 h",
    "hor.cierra": "Irekita · {hora}etan ixten du",
    "hor.abre": "Itxita · {hora}etan irekitzen du",
    "hor.cerrada": "Orain itxita",
    "hor.publicado": "Argitaratutako ordutegia: {horario}. Jaiegunetan alda daiteke.",
    "fav.poner": "Gogokoa",
    "fav.quitar": "Gogokoetatik kendu",
    "compartir": "Partekatu",
    "js.guardado": "Gordeta",
    "js.copiado": "Esteka kopiatuta",
    "js.cerrada": "orain itxita",
    "aj.consumo": "Autoaren kontsumoa (litro edo kilo 100 km-ko)",
    "err.consumo": "Kontsumoak 1 eta 40 artean egon behar du.",
    "admin.brent_viejo": "Brent-a ez da eguneratu {fecha}(e)tik: iragarpenak huts egin dezake. Begiratu edukiontziaren erregistroa.",
    "aj.apariencia": "Hizkuntza eta itxura",
    "aj.tema": "Gaia",
    "aj.mapa": "Joateko mapa-aplikazioa",
    "aj.mapa_preguntar": "Galdetu aldiro",
    "aj.mapa_google": "Google Maps",
    "aj.mapa_apple": "Apple Maps",
    "aj.mapa_waze": "Waze",
    "voz.elegir_una_vez": "Aukeratu behar ez izateko, jarri zure aplikazioa <a "
                          "href=\"/ajustes\">Ezarpenetan</a> eta kopiatu berriro lasterbidearen helbidea <a "
                          "href=\"/voz\">Sirirekin</a> orrian.",
    "voz.con_app": "Helbideak dagoeneko <b>{app}</b> irekitzen du, zure Ezarpenetako mapa-aplikazioa. "
                   "Aldatzen baduzu, kopiatu berriro.",
    "voz.sin_app": "Horrela, aldiro galdetuko dizu zein aplikaziorekin joan. Zuzenean joan dadin, aukeratu "
                   "zure mapa-aplikazioa <a href=\"/ajustes\">Ezarpenetan</a> eta itzuli hona helbidea "
                   "kopiatzera.",
    "tema.auto": "Mugikorrarena",
    "tema.claro": "Argia",
    "tema.oscuro": "Iluna",
    "inicio.mas_cercana_abierta": "Irekita dagoen hurbilena",
    "inicio.mas_rentable": "Errentagarriena, {radio} km baino gertuago",
    "inicio.mas_rentable_abierta": "Irekita dagoen errentagarriena, {radio} km baino gertuago",
    "inicio.rentable_viaje": "Joan-etorria kontuan hartuta: {coste}",
    "inst.titulo": "Izan ezazu aplikazio gisa",
    "inst.texto": "Hasierako pantailatik pantaila osoan irekitzen da. Ia ez du lekurik hartzen.",
    "inst.ios_1": "Sakatu {icono} <b>Partekatu</b> Safariren barran.",
    "inst.ios_2": "Aukeratu {icono} <b>Gehitu hasierako pantailan</b>.",
    "inst.ios_3": "Sakatu <b>Gehitu</b>.",
    "inst.otra_app": "Hemendik ezin da instalatu: ireki Safarin edo Chromen.",
    "inst.instalar": "Instalatu",
    "inst.cerrar": "Orain ez",
    "aj.instalar": "Aplikazioa instalatu",
    "inst.otro_1": "Ireki nabigatzailearen menua {icono}.",
    "inst.otro_2": "Aukeratu <b>Instalatu aplikazioa</b> edo <b>Gehitu hasierako pantailan</b>.",
    "aj.instalada": "Pumpcast aplikazio gisa instalatuta duzu jada.",
}
