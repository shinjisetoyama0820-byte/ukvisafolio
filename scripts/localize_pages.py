# -*- coding: utf-8 -*-
"""Build English and Hindi copies of the static pages, and add the language switch."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "index.html",
    "family.html",
    "documents.html",
    "guides.html",
    "methods.html",
    "apps.html",
    "stratovisa.html",
]
# Japanese source -> (English, Hindi). Exact text nodes and attribute values only.
TEXT = {
"英国ビザの必要書類・申請方法・準備ガイド | UK VISA FOLIO": ("UK visa documents, steps and preparation | UK VISA FOLIO", "यूके वीज़ा के दस्तावेज़, कदम और तैयारी | UK VISA FOLIO"),
"英国ビザの必要書類、費用、申請方法を日本語でわかりやすく解説。": ("A plain-language guide to UK visa documents, fees and the application steps.", "यूके वीज़ा के दस्तावेज़, शुल्क और आवेदन के कदमों की सरल गाइड।"),
"ホーム": ("Home", "होम"),
"配偶者・家族ビザ": ("Spouse and family visa", "जीवनसाथी और परिवार वीज़ा"),
"必要書類": ("Documents", "दस्तावेज़"),
"解説記事": ("Guides", "गाइड"),
"英国ビザの準備を、": ("Prepare for a UK visa,", "यूके वीज़ा की तैयारी,"),
"もっとわかりやすく。": ("in plain language.", "आसान भाषा में।"),
"必要書類・申請費用・手順から、あなたに合った準備方法まで。英国ビザの情報を日本語で整理しました。": ("Documents, fees, steps, and ways to get ready. This site organises UK visa information in English.", "दस्तावेज़, शुल्क, कदम और तैयारी के तरीके। यह साइट यूके वीज़ा की जानकारी हिन्दी में समेटती है।"),
"配偶者ビザの準備を調べる →": ("Look up spouse visa preparation →", "जीवनसाथी वीज़ा की तैयारी देखें →"),
"必要書類を見る": ("See documents", "दस्तावेज़ देखें"),
"英国ビザの種類から探す": ("Start from the visa type", "वीज़ा के प्रकार से शुरू करें"),
"申請したいビザから、必要な情報に進めます。": ("Open the information for the visa you want to apply for.", "जिस वीज़ा के लिए आवेदन करना है, उसकी जानकारी खोलें।"),
"家族・パートナーのためのビザ情報。": ("Information for a partner or family route.", "साथी या परिवार के रास्ते की जानकारी।"),
"詳しく見る →": ("Read more →", "और पढ़ें →"),
"就労ビザ": ("Work visa", "कार्य वीज़ा"),
"Skilled Workerなどの基本情報。": ("Starting points for Skilled Worker and similar routes.", "Skilled Worker और मिलते-जुलते रास्तों की शुरुआती जानकारी।"),
"学生ビザ": ("Student visa", "छात्र वीज़ा"),
"Student visaの申請準備を確認。": ("See what to prepare for a Student visa.", "Student visa की तैयारी देखें।"),
"準備に役立つガイド": ("Guides for getting ready", "तैयारी में काम आने वाली गाइड"),
"検索で気になる疑問を、順番に解決します。": ("Work through the questions people look up, one at a time.", "लोग जो सवाल खोजते हैं, उन्हें एक-एक करके देखें।"),
"必要書類ガイド": ("Document guide", "दस्तावेज़ गाइड"),
"証明書類・翻訳・整理方法を解説。": ("How to sort evidence, translations and files.", "सबूत, अनुवाद और फ़ाइलें कैसे सजाएँ।"),
"申請手順と費用": ("Steps and fees", "कदम और शुल्क"),
"申請前に確認したい手続きと費用。": ("The steps and fees to check before you apply.", "आवेदन से पहले देखने वाले कदम और शुल्क।"),
"よくある疑問": ("Common questions", "आम सवाल"),
"公式情報の調べ方と注意点。": ("How to read the official information, and what to watch.", "आधिकारिक जानकारी कैसे पढ़ें, और किस बात का ध्यान रखें।"),
"ビザ準備方法の比較": ("Ways to prepare", "तैयारी के तरीके"),
"自分で準備する・アプリを使う・専門家に相談する。それぞれの違いを紹介。": ("Prepare it yourself, use an app, or speak with a qualified adviser. This page sets out the difference.", "खुद तैयार करें, ऐप का उपयोग करें, या योग्य सलाहकार से बात करें। अंतर यहाँ है।"),
"アプリで準備する": ("Prepare with an app", "ऐप से तैयारी"),
"書類整理や準備を支援するツールを活用。": ("Use a tool that helps organise the documents.", "दस्तावेज़ सजा़ने में मदद करने वाला टूल उपयोग करें।"),
"自分で準備する": ("Prepare it yourself", "खुद तैयारी करें"),
"自分で準備": ("Prepare it yourself", "खुद तैयारी"),
"アプリで準備": ("Prepare with an app", "ऐप से तैयारी"),
"公式情報を参照して自力で進める方法。": ("Follow the official information and manage it yourself.", "आधिकारिक जानकारी देखकर खुद आगे बढ़ें।"),
"専門家に相談する": ("Speak with an adviser", "सलाहकार से बात करें"),
"複雑な事情や法的判断が必要な場合。": ("When the situation is complex or you need a legal judgement.", "जब स्थिति जटिल हो, या कानूनी निर्णय चाहिए।"),
"英国ビザの準備をもっとスマートに。": ("A calmer way to prepare a UK visa.", "यूके वीज़ा की तैयारी को अधिक व्यवस्थित बनाएँ।"),
"Stratovisaを使って、必要書類の整理や申請準備をスムーズに。": ("Stratovisa helps you organise documents and the preparation steps.", "Stratovisa दस्तावेज़ और तैयारी के कदमों को व्यवस्थित करने में मदद करता है।"),
"UK VISA FOLIO 特典": ("UK VISA FOLIO offer", "UK VISA FOLIO ऑफ़र"),
"お住まいの地域に合うクーポンをコピーしてください。": ("Copy the code for the country where you live.", "जिस देश में आप रहते हैं, उसका कोड कॉपी करें।"),
"日本在住者向け": ("Living in Japan", "जापान में रहने वाले"),
"日本在住者向け申込ページ →": ("Signup page for people in Japan →", "जापान में रहने वालों का साइनअप →"),
"英国在住者向け": ("Living in the UK", "यूके में रहने वाले"),
"英国在住者向け申込ページ →": ("Signup page for people in the UK →", "यूके में रहने वालों का साइनअप →"),
"Stratovisaの詳細・使い方を見る →": ("See what Stratovisa does →", "Stratovisa क्या करता है, देखें →"),
"申請準備を効率化したい方へ": ("If you want the preparation in one place", "अगर तैयारी एक जगह करनी है"),
"Stratovisaは英国ビザの申請準備を支援する民間サービスです。利用前に、対象ビザ・機能・料金を確認しましょう。": ("Stratovisa is a private service that helps you prepare a UK visa application. Check the visas, features and price before you use it.", "Stratovisa एक निजी सेवा है, जो यूके वीज़ा की तैयारी में मदद करती है। उपयोग से पहले वीज़ा, सुविधाएँ और कीमत देख लें।"),
"Stratovisaについて見る →": ("About Stratovisa →", "Stratovisa के बारे में →"),
"※当サイトはStratovisaへの送客を目的としています。": ("This site introduces people to Stratovisa.", "यह साइट लोगों को Stratovisa तक पहुँचाती है।"),
"© 2026 UK VISA FOLIO ｜ 英国ビザの申請準備に関する情報メディア": ("© 2026 UK VISA FOLIO | A guide to preparing a UK visa application", "© 2026 UK VISA FOLIO | यूके वीज़ा की तैयारी की जानकारी"),
"本サイトは英国政府の公式サイトではありません。Stratovisaへの送客を目的とした商業的関係があります。申請条件・費用は必ず": ("This site is not a UK government website. It has a commercial relationship that introduces people to Stratovisa. Check the conditions and fees on ", "यह साइट यूके सरकार की वेबसाइट नहीं है। Stratovisa तक लोगों को पहुँचाने का व्यावसायिक संबंध है। शर्तें और शुल्क यहाँ देखें: "),
"で確認してください。": (".", "।"),
"英国配偶者・家族ビザの申請準備 | UK VISA FOLIO": ("Preparing a UK spouse or family visa | UK VISA FOLIO", "यूके जीवनसाथी या परिवार वीज़ा की तैयारी | UK VISA FOLIO"),
"英国配偶者・家族ビザの条件、必要書類、収入・関係証明、申請準備の流れを日本語で解説。公式情報へのリンクと準備方法の比較も掲載。": ("Conditions, documents, income and relationship evidence, and the preparation steps for a UK spouse or family visa, with links to the official pages.", "यूके जीवनसाथी या परिवार वीज़ा की शर्तें, दस्तावेज़, आय और रिश्ते के सबूत, और तैयारी के कदम। आधिकारिक पन्नों के लिंक के साथ।"),
"申請ガイド": ("Application guide", "आवेदन गाइड"),
"英国ビザ最新情報": ("UK visa updates", "यूके वीज़ा की नई जानकारी"),
"英国配偶者・家族ビザの申請準備ガイド": ("Guide to preparing a UK spouse or family visa", "यूके जीवनसाथी या परिवार वीज़ा की तैयारी"),
"英国でパートナーや家族と暮らすためのビザ。申請前に確認したい条件・証明書類・準備の流れを日本語で整理しました。": ("A visa for living in the UK with a partner or family. This page organises the conditions, evidence and preparation steps to check before you apply.", "यूके में साथी या परिवार के साथ रहने का वीज़ा। आवेदन से पहले देखने वाली शर्तें, सबूत और तैयारी के कदम यहाँ हैं।"),
"最終確認：2026年10月17日": ("Last checked: 17 October 2026", "आखिरी जाँच: 17 अक्टूबर 2026"),
"英国の移民制度は変更されることがあります。本ページは一般的な情報であり、個別の移民法上の助言ではありません。実際の申請では必ず": ("UK immigration rules can change. This page is general information and is not advice on your own case. Before you apply, read the latest ", "यूके के आप्रवासन नियम बदल सकते हैं। यह पृष्ठ सामान्य जानकारी है, आपके अपने मामले की सलाह नहीं। आवेदन से पहले ताज़ा जानकारी पढ़ें: "),
"英国政府の最新情報": ("UK government information", "यूके सरकार की जानकारी"),
"を確認してください。": (".", "।"),
"配偶者・パートナー": ("Spouse or partner", "जीवनसाथी या साथी"),
"収入要件": ("Income", "आय"),
"関係証明": ("Relationship evidence", "रिश्ते का सबूत"),
"01｜まず、対象になる申請ルートを確認": ("01. Check which route you are looking at", "01. देखें कि कौन सा रास्ता आपके मामले से जुड़ता है"),
"「家族ビザ」は一つの条件で全員が申請するものではありません。英国にいる相手の在留資格、婚姻・交際関係、申請場所によって条件が異なります。": ("A family visa is not one set of conditions for everyone. The conditions differ with your partner's status in the UK, your relationship, and where you apply from.", "परिवार वीज़ा सबके लिए एक जैसी शर्त नहीं है। शर्तें यूके में साथी की स्थिति, आपके रिश्ते, और आवेदन की जगह पर निर्भर करती हैं।"),
"確認すること": ("What to check", "क्या देखें"),
"チェックする内容": ("What it covers", "इसमें क्या आता है"),
"相手の英国での資格": ("Your partner's status in the UK", "यूके में साथी की स्थिति"),
"英国・アイルランド国籍、永住資格、その他対象となる在留資格など": ("British or Irish citizenship, settled status, or another status the route covers", "ब्रिटिश या आयरिश नागरिकता, सेटल्ड स्टेटस, या वह स्थिति जिसे यह रास्ता कवर करता है"),
"二人の関係": ("Your relationship", "आपका रिश्ता"),
"婚姻・シビルパートナーシップ・対象となる継続的なパートナー関係など": ("Marriage, a civil partnership, or another lasting partner relationship the route covers", "विवाह, सिविल पार्टनरशिप, या वह साथी संबंध जिसे यह रास्ता कवर करता है"),
"居住予定": ("Where you plan to live", "आप कहाँ रहने की योजना बना रहे हैं"),
"英国で一緒に暮らす予定があるか": ("Whether you plan to live together in the UK", "क्या आप यूके में साथ रहने की योजना बना रहे हैं"),
"その他の要件": ("Other points on the official page", "आधिकारिक पृष्ठ की अन्य बातें"),
"収入・英語力・住居・過去の在留歴など": ("Income, English, housing, and previous immigration history", "आय, अंग्रेज़ी, आवास, और पहले का आप्रवासन इतिहास"),
"参考：": ("Source:", "स्रोत:"),
"02｜準備する書類の主な種類": ("02. The main kinds of documents", "02. दस्तावेज़ों के मुख्य प्रकार"),
"次は一般的な分類です。全員にすべて必要という意味ではなく、申請区分・収入の種類・居住歴などにより異なります。": ("These are general groups. They are not a list that every applicant submits. What applies depends on the route, the type of income, and your residence history.", "ये सामान्य समूह हैं। यह ऐसी सूची नहीं है जिसे हर आवेदक जमा करे। क्या लागू होता है, यह रास्ते, आय के प्रकार और रहने के इतिहास पर निर्भर करता है।"),
"書類の種類": ("Type of document", "दस्तावेज़ का प्रकार"),
"具体例": ("Examples", "उदाहरण"),
"確認のポイント": ("What to look at", "किस बात पर ध्यान दें"),
"本人確認 ↗": ("Identity ↗", "पहचान ↗"),
"有効なパスポート、過去の渡航・在留情報": ("A valid passport, and previous travel or residence information", "वैध पासपोर्ट, और पहले की यात्रा या निवास की जानकारी"),
"氏名や過去の申請履歴の整合性": ("Whether names and earlier applications match", "नाम और पहले के आवेदन मेल खाते हैं या नहीं"),
"関係性の証明 ↗": ("Relationship evidence ↗", "रिश्ते का सबूत ↗"),
"婚姻証明、同居・共同支出を示す資料など": ("A marriage document, or papers that show you live together or share costs", "विवाह का दस्तावेज़, या कागज़ जो साथ रहने या साझा खर्च को दिखाते हैं"),
"申請する関係性の条件に沿った証拠か": ("Whether the evidence matches the relationship on your route", "क्या सबूत आपके रास्ते वाले रिश्ते से मेल खाता है"),
"収入・資金の証明 ↗": ("Income or funds ↗", "आय या धन ↗"),
"給与明細、銀行明細、雇用主のレターなど": ("Payslips, bank statements, or a letter from an employer", "पेस्लिप, बैंक स्टेटमेंट, या नियोक्ता का पत्र"),
"該当する収入区分の規定に沿っているか": ("Whether it matches the income category on the official page", "क्या यह आधिकारिक पृष्ठ की आय श्रेणी से मेल खाता है"),
"英語力の証明 ↗": ("English ↗", "अंग्रेज़ी ↗"),
"認められる試験結果・免除根拠など": ("An accepted test result, or the basis for an exemption", "स्वीकृत परीक्षा परिणाम, या छूट का आधार"),
"申請区分に合う要件か": ("Whether it matches the route", "क्या यह रास्ते से मेल खाता है"),
"翻訳 ↗": ("Translation ↗", "अनुवाद ↗"),
"英語・ウェールズ語以外の書類の認証翻訳": ("A certified translation of documents that are not in English or Welsh", "अंग्रेज़ी या वेल्श के अलावा दस्तावेज़ों का प्रमाणित अनुवाद"),
"公式の翻訳要件を満たすか": ("Whether it meets the translation rules on the official page", "क्या यह आधिकारिक पृष्ठ के अनुवाद नियमों पर खरा उतरता है"),
"必要書類ガイドで準備方法を確認する →": ("See how to prepare documents →", "दस्तावेज़ कैसे तैयार करें →"),
"03｜申請準備の流れ": ("03. How the preparation moves", "03. तैयारी कैसे आगे बढ़ती है"),
"対象ビザと条件を確認：": ("Check the route and the conditions:", "रास्ता और शर्तें देखें:"),
"自分の申請区分を英国政府の案内で確定する。": ("Use the UK government guidance to identify your route.", "अपना रास्ता यूके सरकार की गाइड से पहचानें।"),
"必要な証拠を整理：": ("Sort the evidence:", "सबूत सजाएँ:"),
"本人確認、関係性、収入などの書類を洗い出す。": ("List identity, relationship, income and the other documents for your route.", "पहचान, रिश्ता, आय और अपने रास्ते के अन्य दस्तावेज़ों की सूची बनाएँ।"),
"不足・不一致を確認：": ("Look for gaps and mismatches:", "कमी और मेल न खाने वाली बातें देखें:"),
"氏名表記、日付、証明期間、翻訳の有無を点検する。": ("Check names, dates, the period covered, and whether a translation is included.", "नाम, तारीख, अवधि, और अनुवाद शामिल है या नहीं, यह देखें।"),
"公式サイトから申請：": ("Apply on the official site:", "आधिकारिक साइट पर आवेदन करें:"),
"該当するオンライン申請を行い、案内に従って書類を提出する。": ("Complete the online application for your route and submit documents as the guidance describes.", "अपने रास्ते का ऑनलाइन आवेदन पूरा करें और गाइड के अनुसार दस्तावेज़ दें।"),
"本人確認と結果待ち：": ("Identity check, then the decision:", "पहचान की जाँच, फिर निर्णय:"),
"必要な生体情報の提供等を行い、審査結果を待つ。": ("Provide biometric information where the process asks for it, and wait for the decision.", "जहाँ प्रक्रिया बायोमेट्रिक जानकारी माँगे, वहाँ दें, और निर्णय की प्रतीक्षा करें।"),
"ビザ申請そのものは英国政府の正式な手続きに従って進めます。民間アプリは政府の申請システムや法的助言の代わりにはなりません。": ("The visa application itself follows the UK government's process. A private app does not replace the government system or legal advice.", "वीज़ा आवेदन खुद यूके सरकार की प्रक्रिया से आगे बढ़ता है। एक निजी ऐप सरकारी सिस्टम या कानूनी सलाह की जगह नहीं लेता।"),
"04｜自分で準備する？ アプリを使う？": ("04. Prepare it yourself, or use an app?", "04. खुद तैयार करें, या ऐप उपयोग करें?"),
"方法": ("Approach", "तरीका"),
"向いているケース": ("When it fits", "कब यह उपयुक्त है"),
"注意点": ("Watch for", "ध्यान दें"),
"自分で準備 ↗": ("Prepare it yourself ↗", "खुद तैयारी ↗"),
"公式情報を読み、書類を自分で管理できる": ("You can read the official information and manage the documents", "आप आधिकारिक जानकारी पढ़ सकते हैं और दस्तावेज़ खुद संभाल सकते हैं"),
"確認や整理の時間が必要": ("Reading and sorting take time", "पढ़ने और सजाने में समय लगता है"),
"アプリで準備 ↗": ("Prepare with an app ↗", "ऐप से तैयारी ↗"),
"必要書類を整理しながら進めたい": ("You want to organise the documents as you go", "आप दस्तावेज़ों को साथ-साथ सजा़ना चाहते हैं"),
"サービスごとに対応範囲が異なる": ("Each service covers a different range", "हर सेवा की सीमा अलग होती है"),
"専門家に相談": ("Speak with an adviser", "सलाहकार से बात करें"),
"複雑な事情や法的判断が必要": ("The situation is complex, or you need a legal judgement", "स्थिति जटिल है, या कानूनी निर्णय चाहिए"),
"相談範囲・資格・費用を確認": ("Check what they advise on, their registration, and the fee", "वे किस पर सलाह देते हैं, उनका पंजीकरण, और शुल्क देखें"),
"書類の準備を、整理して進めたい方へ。": ("If you want the documents organised as you prepare.", "अगर दस्तावेज़ों को तैयारी के साथ सजा़ना है।"),
"Stratovisaは英国ビザ申請の準備を支援する民間サービスです。対応する機能と料金、利用前に確認すべき点をまとめました。": ("Stratovisa is a private service that helps you prepare a UK visa application. This page sets out the features, the price, and what to check first.", "Stratovisa एक निजी सेवा है, जो यूके वीज़ा आवेदन की तैयारी में मदद करती है। सुविधाएँ, कीमत, और पहले क्या देखें, यह यहाँ है।"),
"Stratovisaの機能・料金を見る →": ("See Stratovisa features and price →", "Stratovisa की सुविधाएँ और कीमत देखें →"),
"※本サイトはStratovisaへの送客を目的とした商業的関係があります。": ("This site has a commercial relationship that introduces people to Stratovisa.", "इस साइट का Stratovisa तक लोगों को पहुँचाने का व्यावसायिक संबंध है।"),
"05｜よくある質問": ("05. Common questions", "05. आम सवाल"),
"結婚していれば必ず申請できますか？": ("Does being married mean you can apply?", "शादी हो जाने से क्या आवेदन हो जाता है?"),
"婚姻の事実だけでは決まりません。相手の在留資格、関係性、英語力、資金などの該当要件を確認してください。": ("Marriage on its own does not decide it. Check your partner's status, the relationship, English and funds against the route on GOV.UK.", "केवल शादी से यह तय नहीं होता। साथी की स्थिति, रिश्ता, अंग्रेज़ी और धन को GOV.UK के रास्ते से मिलाकर देखें।"),
"日本語の証明書はそのまま使えますか？": ("Can a certificate in another language be used as it is?", "क्या दूसरी भाषा का प्रमाणपत्र वैसे ही चल जाता है?"),
"英語またはウェールズ語以外の書類には、要件を満たす認証翻訳が必要となる場合があります。公式案内を確認してください。": ("Documents that are not in English or Welsh may need a certified translation that meets the official rules. Check the official guidance.", "जो दस्तावेज़ अंग्रेज़ी या वेल्श में नहीं हैं, उनके लिए आधिकारिक नियमों वाला प्रमाणित अनुवाद माँगा जा सकता है। आधिकारिक गाइड देखें।"),
"Stratovisaを使えばビザが承認されますか？": ("Does using Stratovisa mean the visa is granted?", "क्या Stratovisa उपयोग करने से वीज़ा मिल जाता है?"),
"いいえ。ビザの可否を判断するのは英国当局です。書類準備サービスの利用は承認を保証しません。": ("No. The UK authorities decide the application. Using a document-preparation service does not guarantee a grant.", "नहीं। आवेदन का निर्णय यूके की संस्था करती है। दस्तावेज़ तैयारी की सेवा मंज़ूरी की गारंटी नहीं है।"),
"公式情報・参考リンク": ("Official pages", "आधिकारिक पृष्ठ"),
"配偶者・パートナーとして申請する条件（GOV.UK）↗": ("Apply as a partner or spouse (GOV.UK) ↗", "साथी या जीवनसाथी के रूप में आवेदन (GOV.UK) ↗"),
"必要な情報と証明書類（GOV.UK）↗": ("Information and evidence (GOV.UK) ↗", "जानकारी और सबूत (GOV.UK) ↗"),
"家族ビザの総合案内（GOV.UK）↗": ("Family visas (GOV.UK) ↗", "परिवार वीज़ा (GOV.UK) ↗"),
"UK VISA FOLIOは英国政府の公式サイトではありません。法令・料金・審査期間は変更されるため、申請前に必ず公式情報を再確認してください。": ("UK VISA FOLIO is not a UK government website. Rules, fees and processing times change, so read the official pages again before you apply.", "UK VISA FOLIO यूके सरकार की वेबसाइट नहीं है। नियम, शुल्क और प्रोसेसिंग समय बदलते हैं, इसलिए आवेदन से पहले आधिकारिक पृष्ठ फिर पढ़ें।"),
"英国ビザの必要書類ガイド | UK VISA FOLIO": ("UK visa document guide | UK VISA FOLIO", "यूके वीज़ा दस्तावेज़ गाइड | UK VISA FOLIO"),
"英国ビザの必要書類ガイド": ("UK visa document guide", "यूके वीज़ा दस्तावेज़ गाइड"),
"申請区分ごとに書類が異なるため、公式要件を確認しながら準備しましょう。": ("Documents differ by route, so prepare them alongside the official requirements.", "दस्तावेज़ रास्ते के अनुसार बदलते हैं, इसलिए आधिकारिक शर्तों के साथ तैयारी करें।"),
"書類準備の基本ステップ": ("Basic steps for the documents", "दस्तावेज़ों के बुनियादी कदम"),
"申請するビザの種類を確定する": ("Identify the visa you will apply for", "जिस वीज़ा के लिए आवेदन करना है, उसे पहचानें"),
"GOV.UKで該当する申請要件を確認する": ("Read the requirements for that route on GOV.UK", "उस रास्ते की शर्तें GOV.UK पर पढ़ें"),
"身分証明・関係証明・資金証明など必要な資料を整理する": ("Sort identity, relationship, funds and the other papers for your route", "पहचान, रिश्ता, धन और अपने रास्ते के अन्य कागज़ सजाएँ"),
"必要に応じて翻訳や形式の要件を確認する": ("Check translation and format rules where they apply", "जहाँ लागू हों, अनुवाद और फ़ॉर्मैट के नियम देखें"),
"提出前に内容・有効期限・不足を確認する": ("Before you submit, check the contents, expiry dates and anything missing", "जमा करने से पहले सामग्री, वैधता की तारीख और कमी देखें"),
"関係性の証明、収入・住居等の要件に関する資料など、状況に応じた証拠が必要です。": ("Relationship, income, housing and other evidence depends on the situation. GOV.UK sets out what that route asks for.", "रिश्ता, आय, आवास और अन्य सबूत स्थिति पर निर्भर करते हैं। GOV.UK बताता है कि वह रास्ता क्या माँगता है।"),
"配偶者ビザガイド": ("Spouse visa guide", "जीवनसाथी वीज़ा गाइड"),
"へ。": (".", "।"),
"書類整理に使う方法": ("Ways to organise the documents", "दस्तावेज़ सजा़ने के तरीके"),
"紙のチェックリスト、フォルダ管理、申請準備ツールなどから選べます。": ("You can use a paper checklist, folders, or a preparation tool.", "आप कागज़ की चेकलिस्ट, फ़ोल्डर, या तैयारी का टूल उपयोग कर सकते हैं।"),
"アプリ比較": ("App comparison", "ऐप की तुलना"),
"も参考にしてください。": (".", "।"),
"このページは一般的な準備手順です。特定の申請で必要な書類の完全な一覧ではありません。": ("This page is a general preparation sequence. It is not the full document list for a particular application.", "यह पृष्ठ तैयारी का सामान्य क्रम है। यह किसी एक आवेदन की पूरी दस्तावेज़ सूची नहीं है।"),
"英国ビザの申請手順・費用・よくある質問 | UK VISA FOLIO": ("UK visa steps, fees and common questions | UK VISA FOLIO", "यूके वीज़ा के कदम, शुल्क और आम सवाल | UK VISA FOLIO"),
"英国ビザの申請手順・費用・よくある質問": ("UK visa steps, fees and common questions", "यूके वीज़ा के कदम, शुल्क और आम सवाल"),
"申請準備の全体像と、公式情報を確認するためのガイドです。": ("An overview of the preparation, and where to check the official information.", "तैयारी का पूरा चित्र, और आधिकारिक जानकारी कहाँ देखें।"),
"基本的な申請の流れ": ("The basic sequence", "बुनियादी क्रम"),
"該当するビザ区分を確認": ("Check which visa route applies", "देखें कि कौन सा वीज़ा रास्ता लागू होता है"),
"条件・費用・必要書類を確認": ("Check the conditions, fees and documents", "शर्तें, शुल्क और दस्तावेज़ देखें"),
"書類と証拠を準備": ("Prepare the documents and evidence", "दस्तावेज़ और सबूत तैयार करें"),
"公式手続きに従って申請": ("Apply by following the official process", "आधिकारिक प्रक्रिया के अनुसार आवेदन करें"),
"必要に応じて本人確認等を実施": ("Complete an identity check where the process includes one", "जहाँ प्रक्रिया में हो, पहचान की जाँच पूरी करें"),
"結果を待つ": ("Wait for the decision", "निर्णय की प्रतीक्षा करें"),
"就労ビザ（Skilled Worker）": ("Work visa (Skilled Worker)", "कार्य वीज़ा (Skilled Worker)"),
"スポンサー要件、職種、給与要件などを公式サイトで確認してください。": ("Check the sponsor, job and pay points on the official page.", "प्रायोजक, नौकरी और वेतन की बातें आधिकारिक पृष्ठ पर देखें।"),
"学生ビザ（Student）": ("Student visa (Student)", "छात्र वीज़ा (Student)"),
"CAS、資金要件、英語力などを確認してください。": ("Check the CAS, funds and English points.", "CAS, धन और अंग्रेज़ी की बातें देखें।"),
"よくある質問": ("Common questions", "आम सवाल"),
"申請費用はいくら？": ("How much is the fee?", "शुल्क कितना है?"),
"ビザ区分・申請場所・追加費用などによって異なります。公式料金表を確認してください。": ("It depends on the visa, where you apply, and any extra fees. Use the official fee table.", "यह वीज़ा, आवेदन की जगह और अतिरिक्त शुल्क पर निर्भर करता है। आधिकारिक शुल्क तालिका देखें।"),
"審査期間は？": ("How long does a decision take?", "निर्णय में कितना समय लगता है?"),
"申請区分と時期により異なります。": ("It depends on the route and the time you apply.", "यह रास्ते और आवेदन के समय पर निर्भर करता है।"),
"公式の審査期間案内 ↗": ("Official processing times ↗", "आधिकारिक प्रोसेसिंग समय ↗"),
"ビザ準備方法の比較 | UK VISA FOLIO": ("Ways to prepare a visa | UK VISA FOLIO", "वीज़ा तैयारी के तरीके | UK VISA FOLIO"),
"自分で準備・アプリ利用・専門家への相談を、目的別に整理します。": ("Prepare it yourself, use an app, or speak with an adviser. This page sorts those choices.", "खुद तैयारी, ऐप, या सलाहकार। यह पृष्ठ इन विकल्पों को अलग करता है।"),
"向いている人": ("Who it suits", "यह किसके लिए उपयुक्त है"),
"公式情報を読み、自分で管理できる人": ("Someone who can read the official information and manage it", "जो आधिकारिक जानकारी पढ़कर खुद संभाल सके"),
"要件確認や書類管理は自分で行う": ("You check the requirements and manage the documents", "शर्तें और दस्तावेज़ आप खुद देखते हैं"),
"書類整理の手間を減らしたい人": ("Someone who wants less time spent sorting documents", "जो दस्तावेज़ सजा़ने में कम समय लगाना चाहे"),
"サービスの対応範囲・料金を確認する": ("Check what the service covers, and the price", "सेवा की सीमा और कीमत देखें"),
"複雑な事情や法的判断が必要な人": ("Someone with a complex situation, or who needs a legal judgement", "जिसकी स्थिति जटिल हो, या जिसे कानूनी निर्णय चाहिए"),
"資格・登録状況・費用を確認する": ("Check their qualification, registration and fee", "योग्यता, पंजीकरण और शुल्क देखें"),
"GOV.UKで申請条件を確認し、必要書類を管理する方法です。": ("You check the conditions on GOV.UK and manage the documents yourself.", "आप शर्तें GOV.UK पर देखते हैं और दस्तावेज़ खुद संभालते हैं।"),
"公式のビザ確認サービス ↗": ("Official visa check ↗", "आधिकारिक वीज़ा जाँच ↗"),
"書類の整理・チェックリストなどの支援範囲を確認します。": ("Check whether the service covers sorting documents, checklists and similar tasks.", "देखें कि सेवा दस्तावेज़ सजा़ने, चेकलिस्ट और ऐसे कामों को कवर करती है या नहीं।"),
"ビザ申請に使えるアプリ比較": ("Apps people use when preparing a visa", "वीज़ा तैयारी में उपयोग होने वाले ऐप"),
"法的助言が必要な場合は、適切な資格・登録のある専門家を検討してください。アプリは法的助言の代替とは限りません。": ("Where you need legal advice, look for an adviser with the right qualification and registration. An app is not a substitute for that advice.", "जहाँ कानूनी सलाह चाहिए, सही योग्यता और पंजीकरण वाला सलाहकार देखें। ऐप उस सलाह का विकल्प नहीं है।"),
"ビザ申請に使えるアプリ比較 | UK VISA FOLIO": ("Apps people use when preparing a visa | UK VISA FOLIO", "वीज़ा तैयारी में उपयोग होने वाले ऐप | UK VISA FOLIO"),
"準備支援サービスと政府公式アプリを混同せず、それぞれの役割を確認します。": ("Keep a preparation service separate from a government app, and check what each one does.", "तैयारी की सेवा और सरकारी ऐप को अलग रखें, और देखें कि प्रत्येक क्या करता है।"),
"サービス": ("Service", "सेवा"),
"役割": ("Role", "भूमिका"),
"民間の英国ビザ申請準備支援": ("A private service for preparing a UK visa application", "यूके वीज़ा आवेदन की तैयारी की निजी सेवा"),
"対応ビザ・料金・機能を公式サイトで確認": ("Check the visas, price and features on its own site", "वीज़ा, कीमत और सुविधाएँ उसकी अपनी साइट पर देखें"),
"英国政府の本人確認アプリ": ("The UK government's identity app", "यूके सरकार की पहचान ऐप"),
"書類準備を総合的に支援するアプリではない": ("It does not organise the whole document preparation", "यह पूरी दस्तावेज़ तैयारी को व्यवस्थित नहीं करता"),
"英国政府の申請情報・手続き": ("The UK government's application information and process", "यूके सरकार की आवेदन जानकारी और प्रक्रिया"),
"民間の準備支援サービスではない": ("It is not a private preparation service", "यह निजी तैयारी सेवा नहीं है"),
"英国ビザの申請準備を支援する民間サービスです。": ("A private service that helps you prepare a UK visa application.", "यूके वीज़ा आवेदन की तैयारी में मदद करने वाली निजी सेवा।"),
"詳しい紹介と料金": ("The overview and price", "परिचय और कीमत"),
"対象となる申請手続きで本人確認に使用する政府公式アプリです。": ("The government app used for identity checks on the applications it covers.", "उन आवेदनों पर पहचान की जाँच के लिए सरकारी ऐप, जिन्हें यह कवर करता है।"),
"公式説明 ↗": ("Official explanation ↗", "आधिकारिक विवरण ↗"),
"本サイトはStratovisaへの送客を目的としています。比較対象は同じ機能を持つ製品とは限りません。": ("This site introduces people to Stratovisa. The other rows are not products with the same features.", "यह साइट लोगों को Stratovisa तक पहुँचाती है। अन्य पंक्तियाँ समान सुविधाओं वाले उत्पाद नहीं हैं।"),
"Stratovisa｜英国ビザ申請準備の支援サービス | UK VISA FOLIO": ("Stratovisa | Help preparing a UK visa application | UK VISA FOLIO", "Stratovisa | यूके वीज़ा आवेदन की तैयारी | UK VISA FOLIO"),
"Stratovisa｜英国ビザ申請準備の支援サービス": ("Stratovisa | Help preparing a UK visa application", "Stratovisa | यूके वीज़ा आवेदन की तैयारी"),
"対象ビザと料金を確認し、公式サイトで詳しい機能を確認できます。": ("Check the visas and the price, then read the features on the Stratovisa site.", "वीज़ा और कीमत देखें, फिर सुविधाएँ Stratovisa की साइट पर पढ़ें।"),
"対象商品と料金": ("Routes and price", "रास्ते और कीमत"),
"対象": ("Visa", "वीज़ा"),
"参考価格": ("Guide price", "संदर्भ कीमत"),
"価格は共有された商品情報に基づきます。購入時の価格・割引・提供条件は公式サイトでご確認ください。": ("These prices come from the product information shared with this site. Check the price, any discount and the terms on the Stratovisa site before you pay.", "ये कीमतें इस साइट को दी गई उत्पाद जानकारी से हैं। भुगतान से पहले कीमत, छूट और शर्तें Stratovisa की साइट पर देखें।"),
"利用前の確認ポイント": ("What to check before you use it", "उपयोग से पहले क्या देखें"),
"申請予定のビザに対応しているか": ("Whether it covers the visa you plan to apply for", "क्या यह उस वीज़ा को कवर करता है जिसके लिए आप आवेदन करना चाहते हैं"),
"必要な機能・言語が提供されているか": ("Whether the features and language you want are available", "जो सुविधा और भाषा आप चाहते हैं, वह उपलब्ध है या नहीं"),
"どの作業まで支援されるか": ("Which tasks it helps with", "यह किन कामों में मदद करता है"),
"法的助言や申請代行を含むかどうか": ("Whether it includes legal advice or submitting the application for you", "क्या इसमें कानूनी सलाह या आपकी तरफ़ से आवेदन जमा करना शामिल है"),
"Stratovisa公式サイトで確認する ↗": ("Check on the Stratovisa site ↗", "Stratovisa की साइट पर देखें ↗"),
"UK VISA FOLIOはStratovisaへの送客を目的とする情報メディアです。公式サービスそのものではありません。": ("UK VISA FOLIO is an information site that introduces people to Stratovisa. It is not the service itself.", "UK VISA FOLIO एक जानकारी साइट है, जो लोगों को Stratovisa तक पहुँचाती है। यह सेवा खुद नहीं है।"),
"配偶者・家族ビザのイメージ写真": ("Photo suggesting a spouse or family visa", "जीवनसाथी या परिवार वीज़ा का चित्र"),
"就労ビザのイメージ写真": ("Photo suggesting a work visa", "कार्य वीज़ा का चित्र"),
"学生ビザのイメージ写真": ("Photo suggesting a student visa", "छात्र वीज़ा का चित्र"),
"必要書類ガイドのイメージ写真": ("Photo suggesting a document guide", "दस्तावेज़ गाइड का चित्र"),
"申請手順と費用のイメージ写真": ("Photo suggesting steps and fees", "कदम और शुल्क का चित्र"),
"よくある疑問のイメージ写真": ("Photo suggesting common questions", "आम सवालों का चित्र"),
"アプリで準備するのイメージ写真": ("Photo suggesting preparation with an app", "ऐप से तैयारी का चित्र"),
"自分で準備するのイメージ写真": ("Photo suggesting preparing it yourself", "खुद तैयारी का चित्र"),
"専門家に相談するのイメージ写真": ("Photo suggesting a conversation with an adviser", "सलाहकार से बात का चित्र"),
"ビザ申請準備のイメージ": ("Photo suggesting visa preparation", "वीज़ा तैयारी का चित्र"),
"UK Immigration ID Check アプリの画像": ("Image of the UK Immigration ID Check app", "UK Immigration ID Check ऐप की तस्वीर"),
"コピーしました": ("Copied", "कॉपी हो गया"),
"クーポンをコピー": ("Copy the code", "कोड कॉपी करें"),
"TABIDACHIをコピー": ("Copy TABIDACHI", "TABIDACHI कॉपी करें"),
"ISSHONIをコピー": ("Copy ISSHONI", "ISSHONI कॉपी करें"),
}

DISCLAIMER = {
"ja": "Stratovisa は書類整理ツールであり、移民アドバイザーではありません。申請資格の判断や移民に関する助言は行いません。書類の要件はすべて GOV.UK の公開ガイダンスに基づいています。",
"en": "Stratovisa is a document-organisation tool and is not an immigration adviser. It does not decide whether you qualify, and it does not give immigration advice. Document requirements follow published GOV.UK guidance.",
"hi": "Stratovisa दस्तावेज़ व्यवस्थित करने का टूल है। यह आप्रवासन सलाहकार नहीं है। यह पात्रता तय नहीं करता और आप्रवासन सलाह नहीं देता। दस्तावेज़ों की शर्तें GOV.UK की सार्वजनिक गाइड पर आधारित हैं।",
}

EN_COUPON = '''<div style="background:#fff;color:#172f51;border-radius:12px;padding:22px;max-width:520px;margin:24px 0"><div style="font-weight:700">UK VISA FOLIO offer</div><div style="font-size:clamp(36px,5vw,58px);font-weight:900;line-height:1.4">35% OFF</div><p style="font-size:13px;margin:0 0 12px">The 35% discount applies to the Stratovisa service fee. UK government application fees are separate. Choose where you live, and one code is shown.</p><label for="folio-place" style="font-weight:700;font-size:13px">Where do you live?</label><select id="folio-place" style="display:block;width:100%;margin:6px 0 12px;padding:10px;border-radius:6px;border:1px solid #d7dfe9;font:inherit"><option value="">Select a country</option><option value="ng">Nigeria</option><option value="pk">Pakistan</option><option value="uk-ng">United Kingdom, Nigeria code</option><option value="uk-pk">United Kingdom, Pakistan code</option></select><div id="folio-coupon" hidden><div style="display:flex;align-items:center;gap:8px"><code id="folio-code" style="flex:1;background:#f0f3f7;padding:12px;border-radius:6px;font-size:15px"></code><button type="button" id="folio-copy" aria-label="Copy the code" style="border:1px solid #d7dfe9;border-radius:6px;padding:10px 13px;background:#f0f3f7;cursor:pointer">⧉</button></div><a id="folio-signup" href="https://stratovisa.com/en/signup" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin-top:7px;color:#1c5796;text-decoration:underline;font-size:13px">Open the signup page →</a></div></div><script>(function(){var codes={ng:["JAPA","https://stratovisa.com/en/signup?ref=JAPA"],pk:["MUBARAK","https://stratovisa.com/en/signup?ref=MUBARAK"],"uk-ng":["WEDEYHERE","https://stratovisa.com/en/signup?ref=WEDEYHERE"],"uk-pk":["KHUSHAAMDEED","https://stratovisa.com/en/signup?ref=KHUSHAAMDEED"]};var sel=document.getElementById("folio-place"),box=document.getElementById("folio-coupon"),codeEl=document.getElementById("folio-code"),link=document.getElementById("folio-signup"),btn=document.getElementById("folio-copy");if(!sel)return;sel.addEventListener("change",function(){var row=codes[sel.value];if(!row){box.hidden=true;return;}codeEl.textContent=row[0];link.href=row[1];box.hidden=false});btn.addEventListener("click",function(){if(window.copyStratovisaCoupon)copyStratovisaCoupon(codeEl.textContent,btn)})})();</script>'''

HI_COUPON = '''<div style="background:#fff;color:#172f51;border-radius:12px;padding:22px;max-width:520px;margin:24px 0"><div style="font-weight:700">UK VISA FOLIO ऑफ़र</div><div style="font-size:clamp(36px,5vw,58px);font-weight:900;line-height:1.4">35% OFF</div><p style="font-size:13px;margin:0 0 12px">35% की छूट Stratovisa के सेवा शुल्क पर है। यूके सरकार का आवेदन शुल्क अलग है।</p><div style="margin-bottom:16px"><div style="font-weight:700;margin-bottom:5px">भारत में रहने वाले</div><div style="display:flex;align-items:center;gap:8px"><code style="flex:1;min-width:0;background:#f0f3f7;padding:12px;border-radius:6px;font-size:15px">SHUBHARAMBH</code><button type="button" onclick="copyStratovisaCoupon('SHUBHARAMBH',this)" aria-label="SHUBHARAMBH कॉपी करें" style="border:1px solid #d7dfe9;border-radius:6px;padding:10px 13px;background:#f0f3f7;color:#172f51;cursor:pointer;font-size:18px">⧉</button></div><a href="https://stratovisa.com/hi/signup?ref=SHUBHARAMBH" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin-top:7px;color:#1c5796;text-decoration:underline;font-size:13px">भारत में रहने वालों का साइनअप →</a></div><div><div style="font-weight:700;margin-bottom:5px">यूके में रहने वाले</div><div style="display:flex;align-items:center;gap:8px"><code style="flex:1;min-width:0;background:#f0f3f7;padding:12px;border-radius:6px;font-size:15px">NAYAADHYAY</code><button type="button" onclick="copyStratovisaCoupon('NAYAADHYAY',this)" aria-label="NAYAADHYAY कॉपी करें" style="border:1px solid #d7dfe9;border-radius:6px;padding:10px 13px;background:#f0f3f7;color:#172f51;cursor:pointer;font-size:18px">⧉</button></div><a href="https://stratovisa.com/hi/signup?ref=NAYAADHYAY" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin-top:7px;color:#1c5796;text-decoration:underline;font-size:13px">यूके में रहने वालों का साइनअप →</a></div></div>'''

def switch_for(lang, filename):
    labels = (("ja", "日本語"), ("en", "English"), ("hi", "हिन्दी"))
    options = []
    for code, label in labels:
        selected = " selected" if code == lang else ""
        options.append(f'<option value="{public_path(code, filename)}"{selected}>{label}</option>')
    return '<select class="lang-select" data-lang-select aria-label="Change language" onchange="if(this.value)location.href=this.value">' + "".join(options) + "</select>"
JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def public_path(lang, filename):
    stem = filename[:-5]
    rest = "" if stem == "index" else stem
    if lang == "ja":
        return "/" + rest if rest else "/"
    return f"/{lang}/" + rest if rest else f"/{lang}/"


def apply_text(html, lang):
    idx = 0 if lang == "en" else 1
    parts = re.split(r"(<[^>]+>)", html)
    out = []
    for part in parts:
        if part.startswith("<"):
            def repl(match, idx=idx):
                value = match.group(2)
                if value in TEXT:
                    value = TEXT[value][idx]
                return match.group(1) + value + match.group(3)
            out.append(re.sub(r'(=\s*")([^"]*)(")', repl, part))
        else:
            stripped = part.strip()
            if stripped in TEXT:
                out.append(part.replace(stripped, TEXT[stripped][idx], 1))
            else:
                out.append(part)
    html = "".join(out)
    for key in ("コピーしました", "クーポンをコピー", "TABIDACHIをコピー", "ISSHONIをコピー"):
        html = html.replace(key, TEXT[key][idx])
    return html


def swap_coupon(html, lang):
    start = html.find('<div style="background:#fff;color:#172f51;border-radius:12px;padding:22px;max-width:470px;margin:24px 0">')
    end = html.find('<a class="btn" href="stratovisa.html">')
    if start == -1 or end == -1 or end < start:
        return html
    block = EN_COUPON if lang == "en" else HI_COUPON
    return html[:start] + block + html[end:]


def decorate(html, lang, filename):
    html = html.replace('lang="ja"', f'lang="{lang}"', 1)
    if "data-lang-select" not in html and "data-lang-switch" not in html:
        html = html.replace("</nav>", "</nav>" + switch_for(lang, filename), 1)
    links = []
    for code in ("ja", "en", "hi"):
        href = "https://ukvisafolio.com" + public_path(code, filename)
        links.append(f'<link rel="alternate" hreflang="{code}" href="{href}">')
    links.append(f'<link rel="alternate" hreflang="x-default" href="https://ukvisafolio.com{public_path("ja", filename)}">')
    current = "https://ukvisafolio.com" + public_path(lang, filename)
    links.append(f'<link rel="canonical" href="{current}">')
    html = html.replace("</head>", "".join(links) + '<script src="/assets/site.js" defer></script></head>', 1)
    if "data-folio-note" not in html:
        note = f'<p data-folio-note style="margin:10px 0 0">{DISCLAIMER[lang]}</p>'
        if lang == "ja":
            note += '<p style="margin:8px 0 0"><a href="/insights">アクセス状況</a></p>'
        html = html.replace("</div></footer>", note + "</div></footer>", 1)
    if lang == "en":
        html = html.replace(
            "https://stratovisa.com/en?utm_source=ukvisafolio&utm_medium=referral&utm_campaign=jp_content",
            "https://stratovisa.com/en?utm_source=ukvisafolio&utm_medium=referral&utm_campaign=en_folio",
        )
    if lang == "hi":
        html = html.replace(
            "https://stratovisa.com/en?utm_source=ukvisafolio&utm_medium=referral&utm_campaign=jp_content",
            "https://stratovisa.com/hi?utm_source=ukvisafolio&utm_medium=referral&utm_campaign=hi_folio",
        )
        html = html.replace(
            'font-family:system-ui,-apple-system,"Noto Sans JP",sans-serif',
            'font-family:system-ui,"Nirmala UI","Noto Sans Devanagari","Noto Sans JP",sans-serif',
        )
    return html


def leftover(html):
    html = re.sub(r'<div class="lang-switch"[\s\S]*?</div>', "", html)
    found = []
    for part in re.split(r"<[^>]+>", html):
        if JP.search(part):
            found.append(part.strip()[:180])
    return found


def main():
    originals = {name: (ROOT / name).read_text(encoding="utf-8") for name in PAGES}
    problems = []
    for name, source in originals.items():
        for lang in ("en", "hi"):
            html = swap_coupon(source, lang) if name == "index.html" else source
            html = apply_text(html, lang)
            html = decorate(html, lang, name)
            left = leftover(html)
            if left:
                problems.append((lang, name, left))
            folder = ROOT / lang
            folder.mkdir(exist_ok=True)
            (folder / name).write_text(html, encoding="utf-8")
        ja = decorate(source, "ja", name)
        (ROOT / name).write_text(ja, encoding="utf-8")
    if problems:
        for lang, name, left in problems:
            print(f"LEFT {lang} {name}")
            for item in left:
                print(" -", item)
        raise SystemExit(1)
    print("localized", len(PAGES), "pages")


if __name__ == "__main__":
    main()
