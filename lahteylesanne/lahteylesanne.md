### Esmärk
Põhieesmärk on disainida 3-D printerile Ender 3 Pro karp elektroonika mahutamiseks.
Karp peaks olema võimalkult universaalne. Esmases lähenduses peab mahutama sellised detailid:
Orange Pi Lite (http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Lite.html)
BTT SKR 3(https://global.bttwiki.com/SKR%203.html)
### Disain
Ender 3 Pro alusraami moodustab 4040 V-Slots alumiiniumprofiilist H kujuline raam. Kujutame ette et H täht lamab horisontaalselt maas, alumine külg vaataja poole. Elektroonikakarp 
tuleb siis H tähe vaatajapoolsesse ossa (ette). Karbi mõõdud on ca 125x250 mm. Karbi külgedel on V-slottidesse minevad siinid. 
Probleem on selles, et mu maksimaalne prinditav detail on ca 220 mm, siis ma ühes tükis ei saa kujundada seda.
Idee on selles et kujundan kumbagi külje eraldi (peegelpildis), külje küljes on ka näiteks 40mm põhja, mille servas on omakorda soon, kuhu saan siis eraldi trükitud põhja sisse libistada. esipaneeli ning kaanega põhimõtteliselt midagi analoogset. See annab ka selle eelise, et kui mingit plaati välja vahetan ei pea tervet karpi ümber kujundama, saan vastavalt vajadusele ainult esipaneeli(kus on pistikute augud) või põhja (kus on kruviaugud) uue teha.


### Vahendid
Kasutame build123d(https://github.com/gumyr/build123d).
Vajadusel kasutame sobivaid lisandmooduleid.
Iga detail salvestatakse eraldi pythoni faili (ise otsustad, kas on mõistlik moodulitena teha või kuidas iganes). Kogu disain on komplektina on eraldi nö pea failis, kuhu siis vajalikud detailid imporditakse .