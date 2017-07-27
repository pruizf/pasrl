$(document).ready(function() {

    if($("#actionview").parent("li").hasClass("active")){
        if($("#dbpview").parent("li").hasClass("active")){
            get_actions("dbp");
        }
        else if($("#rglview").parent("li").hasClass("active")){
            get_actions("rgl")
        }
        else if($("#kpview").parent("li").hasClass("active")){
            get_actions("kp")
        }
        else if($("#solrdocs").parent("li").hasClass("active")){
            get_actions("doc")
        }
        else {
            get_actions("sen");
        }
    }

    if($("#actorview").parent("li").hasClass("active")){
        if($("#dbpview").parent("li").hasClass("active")){
            get_actors("dbp");
        }
        else if($("#rglview").parent("li").hasClass("active")) {
            get_actors("rgl")
        }
        else if($("#kpview").parent("li").hasClass("active")) {
            get_actors("kp")
        }
        else if($("#solrdocs").parent("li").hasClass("active")) {
            get_actors("doc")
        }
        else {
            get_actors("sen");
        }
    }


    // sortable table headers

    //$(document).on("click", "th", function(e){
    // apply just to th with class "st" for now
    $(document).on("click", ".st", function(e){
	/*if($(this).hasClass("asc")){
	    $(this).removeClass("asc");
	    $(this).addClass("desc");
	}
	else if($(this).hasClass("desc")){
	    $(this).removeClass("desc");
	    $(this).addClass("asc");
	}
	else{
	    $(this).addClass("asc");
	}

	$(this).siblings().removeClass("asc")
	$(this).siblings().removeClass("desc")*/
	sort = $(this).text().toLowerCase()
	
	if($("#actionview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
		get_actions("dbp", sort);
            }
            else if($("#rglview").parent("li").hasClass("active")){
		get_actions("rgl", sort)
            }

            else if($("#kpview").parent("li").hasClass("active")){
		get_actions("kp", sort)
            }
            else if($("#solrdocs").parent("li").hasClass("active")){
		get_actions("doc", sort)
            }
            else {
		get_actions("sen", sort);
            }
	}
	
	if($("#actorview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
		get_actors("dbp", sort);
            }
            else if($("#rglview").parent("li").hasClass("active")) {
		get_actors("kp", sort)
            }
            else if($("#kpview").parent("li").hasClass("active")) {
		get_actors("kp", sort)
            }
            else if($("#solrdocs").parent("li").hasClass("active")) {
		get_actors("doc", sort)
            }
            else {
		get_actors("sen", sort);
            }
	}
	
    });
    
    $("#resetbutton").click(function(){
        location.reload();
    });

    $("#resetbutton2").click(function(){
        location.reload();
    });


    $("#actionview").click(function(){
        $(this).parent("li").addClass("active");
        $("#actorview").parent("li").removeClass("active");
        if($("#dbpview").parent("li").hasClass("active")){
            get_actions("dbp", "default");
        }
        else if($("#rglview").parent("li").hasClass("active")){
            get_actions("rgl", "default");
        }
        else if($("#kpview").parent("li").hasClass("active")){
            get_actions("kp", "default");
        }
        else if($("#solrdocs").parent("li").hasClass("active")){
            get_actions("doc", "default");
        }
        else {
            get_actions("sen", "default");
        }
    });

    $("#actorview").click(function(){
        $(this).parent("li").addClass("active");
        $("#actionview").parent("li").removeClass("active");
        if($("#dbpview").parent("li").hasClass("active")){
            get_actors("dbp", "default");
        }
        else if($("#rglview").parent("li").hasClass("active")){
            get_actors("rgl", "default");
        }
        else if($("#kpview").parent("li").hasClass("active")){
            get_actors("kp", "default");
        }
        else if($("#solrdocs").parent("li").hasClass("active")){
            get_actors("doc", "default");
        }
        else {
            get_actors("sen", "default");
        }
    });

    $("#solrdocs").click(function(){
        $(this).parent("li").addClass("active");
        $("#solrsens").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");
        if($("#actorview").parent("li").hasClass("active")){
            get_actors("doc");
        }
        else {
            get_actions("doc");
        }
    });


    $("#solrsens").click(function(){
        $(this).parent("li").addClass("active");
        $("#solrdocs").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");
        if($("#actorview").parent("li").hasClass("active")){
            get_actors("sen");
        }
        else {
            get_actions("sen");
        }
    });

    $("#dbpview").click(function(){
        $(this).parent("li").addClass("active");
        $("#solrdocs").parent("li").removeClass("active");
        $("#solrsens").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");
        if($("#actorview").parent("li").hasClass("active")){
            get_actors("dbp");
        }
        else {
            get_actions("dbp");
        }
    });

    $("#rglview").click(function(){
        $(this).parent("li").addClass("active");
        $("#solrdocs").parent("li").removeClass("active");
        $("#solrsens").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");
        if($("#actorview").parent("li").hasClass("active")){
            get_actors("rgl");
        }
        else {
            get_actions("rgl");
        }
    });

    $("#kpview").click(function(){
        $(this).parent("li").addClass("active");
        $("#solrdocs").parent("li").removeClass("active");
        $("#solrsens").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        if($("#actorview").parent("li").hasClass("active")){
            get_actors("kp");
        }
        else {
            get_actions("kp");
        }
    });


    $("#left-previous").click(function(){
    pager_prev()
    });

    $("#left-next").click(function(){
    pager_next()
    });

    /*
      Click on tr element : displays Solr document or
      DB sentence depending on whether Docs or Sentences
      tab is active
    */
    $(document).on("click", ".db_record", function(e){
        doc_id = $(this).attr('id');
        sent_id = $(this).attr('sid');
//        if ($("#solrsens").parent("li").hasClass("active")){
//            get_db_sen(sent_id)
//        }
        if($("#solrdocs").parent("li").hasClass("active")){
            get_solr_doc(doc_id, sent_id);
        }
        else{
            get_db_sen(sent_id);
        }
        $(this).css('background-color', '#f5f5f5');
        $(this).siblings().css('background-color', '#fff');
    });


    // agree-disagree kp and dbp click selects sentence

        // or-logic, can only highlight one column at a time (en, rg or kp)
    $(document).on("click", ".en_agd", function(e){
        $(".rg_agd").css('background-color', '#fff')
        $(".ke_agd").css('background-color', '#fff')
    });
    $(document).on("click", ".rg_agd", function(e){
        $(".en_agd").css('background-color', '#fff')
        $(".ke_agd").css('background-color', '#fff')
    });
    $(document).on("click", ".ke_agd", function(e){
        $(".en_agd").css('background-color', '#fff')
        $(".rg_agd").css('background-color', '#fff')
    });

    $(document).on("click", ".en_agd, .rg_agd, .ke_agd", function(e){
        sids = $(this).attr('id');
        label = $(this).children('td.search').text();
        //console.log("label " + label)
        get_sents_for_ek(sids, label)
        // highlight selected row
        $(this).css('background-color', '#f5f5f5'); //try eee if need darker
        $(this).siblings().css('background-color', '#fff');
    })

    // main view kp and dbp click selects propositions

    $(document).on("click", ".ek_main, .se2prop", function(e){
        var ptmids = $(this).attr('id');
        //console.log("point_mention_ids: " + ptmids)
        if ($(this).attr('class') == "ek_main"){
            // get term to highlight from 1st td
            var sq4hl = $(this).closest('tr').find('td:eq(0)').text();
            //console.log("sq4hl: " + sq4hl)
            get_props_for_ek(ptmids, "ek", sq4hl)
        }
        else{
            get_props_for_ek(ptmids, "sen")
        }
        $(this).css('background-color', '#eee'); // try #f5f5f5 if need lighter
        $(this).siblings().css('background-color', '#fff');
    })


    /* Form actions */
    $("#col1-form").submit(function(e){
    pager_reset();

    if($('#col1-form').find("input[name='predicate']").val() != ""){
        $("#actionview").parent("li").addClass("active");
        $("#actorview").parent("li").removeClass("active");
        }
    else{
        $("#actorview").parent("li").addClass("active");
        $("#actionview").parent("li").removeClass("active");
    }

    if($("#actionview").parent("li").hasClass("active")){
        if($("#dbpview").parent("li").hasClass("active")){
            get_actions("dbp");
        }
        else if($("#rglview").parent("li").hasClass("active")){
            get_actions("rgl");
        }
        else if($("#kpview").parent("li").hasClass("active")){
            get_actions("kp");
        }
        else if($("#solrdocs").parent("li").hasClass("active")){
            get_actions("doc");
        }
        else {
            get_actions("sen");
        }
    }

    if($("#actorview").parent("li").hasClass("active")){
        if($("#dbpview").parent("li").hasClass("active")){
            get_actors("dbp");
        }
        else if($("#rglview").parent("li").hasClass("active")){
            get_actors("rgl");
        }
        else if($("#kpview").parent("li").hasClass("active")){
            get_actors("kp");
        }
        else if($("#solrdocs").parent("li").hasClass("active")){
            get_actors("doc");
        }
        else {
            get_actors("sen");
        }
    }
    e.preventDefault();
    return false;
    });

    /* AgreeDisagree form */
    $("#agd-form").submit(function(e){
        get_agree_disagree();
        e.preventDefault();
        return false;
    });


    //Resets 'first' and 'last' session params
    function pager_reset(){
    $.ajax({
        url: '/ui/pager-reset',
        type: 'GET',
        success: function (response) {
        },
        error: function (response) {
        $('#records_table').html("API error 1");
        }
    });
    }

    //Moves to next page (changes 'first' and 'last' session params)
    function pager_next(){
    $.ajax({
        url: '/ui/pager-next',
        type: 'GET',
        success: function (response) {
        if($("#actionview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
            get_actions("dbp");
            }
            else if($("#kpview").parent("li").hasClass("active")){
            get_actions("kp");
            }
            else if($("#solrdocs").parent("li").hasClass("active")){
            get_actions("doc");
            }
            else {
            get_actions("sen");
            }
        }

        if($("#actorview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
            get_actors("dbp");
            }
            else if($("#kpview").parent("li").hasClass("active")){
            get_actors("kp");
            }
            else if($("#solrdocs").parent("li").hasClass("active")){
            get_actors("doc");
            }
            else {
            get_actors("sen");
            }
        }
        },
        error: function (response) {
        $('#records_table').html("API error 2");
        }
    });
    }

    //Moves to previous page (changes 'first' and 'last' session params)
    function pager_prev(){
    $.ajax({
        url: '/ui/pager-prev',
        type: 'GET',
        success: function (response) {
        if($("#actionview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
                get_actions("dbp");
            }
            else if($("#kpview").parent("li").hasClass("active")){
                get_actions("kp");
            }
            else if($("#solrdocs").parent("li").hasClass("active")){
                get_actions("doc");
            }
            else {
                get_actions("sen");
            }
        }

        if($("#actorview").parent("li").hasClass("active")){
            if($("#dbpview").parent("li").hasClass("active")){
                get_actors("dbp");
            }
            else if($("#kpview").parent("li").hasClass("active")){
                get_actors("kp");
            }
            else if($("#solrdocs").parent("li").hasClass("active")){
                get_actors("doc");
            }
            else {
                get_actors("sen");
            }
        }
        },
        error: function (response) {
        $('#records_table').html("API error 3");
        }
    });
    }

    /* http://skipperkongen.dk/2011/01/11/solr-with-jsonp-with-jquery/ */


    function test_sentence(txt){
    console.log("test sentence")
    $.ajax({
        url: '/ui/fullsent/' + txt + '/',
        type: 'GET',
        success: function (response) {
            console.log("id " + txt)
        },
        error: function (response) {
        $('#records_table').html("API error 4");
        }
    });
    }

    // https://stackoverflow.com/questions/14973696 event delegation
    $(document).on("click", "#sentence", function(e){
        test_sentence("1")
        e.preventDefault()
    });


    // add pager arrows, called from get_actors and get_actions
    // (since get_props_for_ek removes the pagers as has no pagination)
    function add_pagers(){
        $("#left-previous").html('<a href="#props">&lt;</a>')
        $("#left-next").html('<a href="#props">&gt;</a>')
    }



    function get_actors(tab, sort){
        var myurl = "/ui/actors/sen/"
        if (tab === 'sen') {
            myurl = '/ui/actors/sen/'
        }
        else if (tab === 'doc') {
            myurl = '/ui/actors/doc/'
        } else if(tab === 'dbp') {
            myurl = '/ui/actors/dbp/'
        } else if(tab === 'rgl') {
            myurl = '/ui/actors/rgl/'
        } else if(tab === 'kp') {
            myurl = '/ui/actors/kp/'
        }

        /*
          Ajout de l'id de la colonne qui
          servira de param pour le tri
         */
        if(sort != undefined){
            myurl += sort + "/";
        }
	    console.log(myurl)

        add_pagers()

        $.ajax({
            //url: param === 'doc' ? '/ui/actors/doc/' : '/ui/actors/dbp',
            url: myurl,
            type: 'GET',
            dataType: 'json',
            data: $('#col1-form').serialize(),
            success: function (response) {

            //console.log("col1-form: " + $('#col1-form').serialize());

            // Records table

            var trs = '<table  class="table .table-striped"><thead class="blabel"><tr>' +
                      // sortable table headers
                      '<th class="st">Actor</th>' +
                      '<th class="st">Action</th>' +
                      '<th class="st">Point</th>' +
                      '<th class="st">COP</th>' +
                      '<th class="st">Year</th>' +
                      '<th class="st" title="Confidence">Conf</th></tr></thead><tbody>'
            // make css class for predicate sensitive to predicate type
            data = response.db_response;
            var totalprops = response.totalprops;
            var curpage = response.curpage
            var totpages = response.totpages
            $("#propcount").html(totalprops + " message")
            if (totalprops > 1 || totalprops === 0){
                $("#propcount").append("s")
            }
            $("#propcount").append("<span style='font-weight:normal;font-style:normal'> [ p " +
                curpage + " / " + totpages + " ]</span>");

            //console.log("NBR RES: " + totalprops)

            $.each(JSON.parse(data), function (i, item) {
                var predclass = "";
                if (item.ptype == "support"){
                    predclass = "supp";
                }
                else if(item.ptype == "oppose"){
                    predclass = "opp";
                }
                else {
                    predclass = "rep";
                }
                var actor2show = item.actor.replace(/_/g, ' ');
                trs += '<tr id="' + item.doc + '" sid="' + item.sid + '" class="db_record">'
                trs += '<td>' + actor2show + '</td>'
                trs += '<td class="' + predclass + '">' + item.predicate + '</td>'
                trs += '<td>' + item.point + '</td>'
                trs += '<td class="cop" title="' + item.city + '">' + item.cop + '</td><td>' + item.year + '</td>';
                trs += '<td class="rcount">' + item.conf + '</td></tr>';

            });
            trs += "</tbody></table>"
            $('#records_table').html(trs);
            docs_content = '<div class="col-sm-12">';
            docs = response.docs;

            // Display Solr Sentences

            if (tab === 'sen'){
                // count of sentences with propositions
                var totalsentences = response.totalsentences;
                $("#rpanelcount").html(totalsentences + " sentence");
                if (totalsentences > 1 || totalsentences === 0){
                    $("#rpanelcount").append("s")
                }
                // count of sentences matching the solr free-text query
                var formqs = $('#col1-form').serialize();
                // only if no prop-query or if a free-text query was entered
                if (formqs.indexOf("actor=&predicate=&point=&") >= 0 ||
                    formqs.indexOf("solrq=") !== formqs.length - "solrq=".length) {
                    $("#rpanelcount").append(
                      "<span style='font-weight:normal;font-style:normal'" +
                      " title='total sentences matching free-text query'>" +
                      " | " +  response.totalsentences_for_solrq + "</span>");
                }
                // sentence table
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;"><thead class="blabel">' +
                                '<th>Sentence</th><th class="st">COP</th><th class="st">Year</th></thead><tbody>'
                var ctr = 1;
                $.each(JSON.parse(docs), function (i, item) {
                    // only make clickable/hover change if HAS propositions
                    var myclass = (item.propidstr !== -1) ? ' class="se2prop"' : '';
                    docs_content += '<tr' + myclass + ' id="' + item.propidstr + '"';
/*                    if (ctr % 2 === 0){
                        docs_content += ' style="background-color:#f0f0f0;"'
                    }*/
                    docs_content += '><td';
                    // css workafound: 1st col of even rows
                    if (ctr %2 !== 0){
                      docs_content += ' class="evsenb"'
                    }
                    docs_content += '>' + item.description + '</td>';
                    docs_content += '<td>' + item.cop + '</td><td';
                    // css workafound: last col of even rows
                    if (ctr %2 !== 0){
                      docs_content += ' class="evsene"'
                    }
                    docs_content += '>' + item.year + '</td></tr>'
                    ctr += 1
                });
            }

            // Display Solr Documents

            else if (tab === 'doc'){
                var totaldocs = response.totaldocs;
                $("#rpanelcount").html(totaldocs + " document");
                if (totaldocs > 1 || totaldocs === 0){
                    $("#rpanelcount").append("s")
                }
                $.each(JSON.parse(docs), function (i, item) {
                    // div won't display correctly if short_text ends with <p,
                    var short_text = item.description.substring(0, 500).split(" ").slice(0, -1).join(" ");
                    if (short_text.match(/<p ?\/?>?$/)){
                        short_text = short_text.replace(/<p ?\/?>?$/, '');
                    }
                    docs_content += '<div class="result-document"><div class="result-title">' +
                                     item.title + '<span class="normaltext" style="float:right;"> [' + item.id +
                                                  ']</span></div><p />' +
                                     //TODO: a "See more" link to see the rest of the document
                                     '<div class="result-body">'  + short_text + ' ...</div></div>';
                });
            }

            // Display DBpedia entities

            else if (tab === 'dbp'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th>' +
                    '<th title="propositions">Count</th></thead><tbody>';
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td><a class="dbkp" href="' + item.wurl + '" target="_blank">' +
                         item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }

            // Display concepts from Reegle Thesaurus (climatetagger api)
            else if (tab === 'rgl'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th>' +
                    '<th title="propositions">Count</th></thead><tbody>';
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td><a class="dbkp" href="' + item.wurl + '" target="_blank">' +
                         item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }

            // Display keyphrases
            else if (tab === 'kp'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th>' +
                    '<th title="propositions">Count</th></thead><tbody>'
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td>' + item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }
            docs_content += "</tbody></table></div>";

            $('#documents').html(docs_content);

            },
            error: function (response) {
                //$('#records_table').html("API error 5");

                /* workaround: hides error message going to MainView
                   from AgreeDisagree, but shows it for a real error
                 */
                setTimeout(function(){
                  $('#records_table').html("API error 5");
                }, 3000);
            }
        });
    }


    function get_actions(tab, sort){
        var myurl = '/ui/actions/sen/'
        if (tab === 'sen') {
            myurl = '/ui/actions/sen/'
        }
        else if (tab === 'doc') {
            myurl = '/ui/actions/doc/'
        } else if(tab === 'dbp') {
            myurl = '/ui/actions/dbp/'
        } else if(tab === 'rgl') {
            myurl = '/ui/actions/rgl/'
        } else if(tab === 'kp') {
            myurl = '/ui/actions/kp/'
        }

        /*
          Ajout de l'id de la colonne qui
          servira de param pour le tri
          'actor' par défaut
         */
        if(sort != undefined){
            myurl += sort + "/";
        }
        console.log(myurl)

        add_pagers()

        $.ajax({
            url: myurl,
            type: 'GET',
            dataType: 'json',
            data: $('#col1-form').serialize(),
            success: function (response) {

            // Records table

            var trs = '<table  class="table .table-striped"><thead class="blabel"><tr>' +
                      // sortable table headers
                      '<th class="st">ActionType</th>' +
                      '<th class="st">Actor</th>' +
                      '<th class="st">Point</th>' +
                      '<th class="st">COP</th>' +
                      '<th class="st">Year</th>' +
                      '<th class="st" title="Confidence">Conf</th></tr></thead><tbody>';
            // make css class for predicate sensitive to predicate type
            data = response.db_response;
            var totalprops = response.totalprops;
            var curpage = response.curpage
            var totpages = response.totpages
            $("#propcount").html(totalprops + " message")
            if (totalprops > 1 || totalprops === 0){
                $("#propcount").append("s")
            }
            $("#propcount").append("<span style='font-weight:normal;font-style:normal'> [ p " +
                curpage + " / " + totpages + " ]</span>");
            $.each(JSON.parse(data), function (i, item) {
                var predclass = "";
                if (item.ptype == "support"){
                    predclass = "supp";
                }
                else if(item.ptype == "oppose"){
                    predclass = "opp";
                }
                else {
                    predclass = "rep";
                }
                var actor2show = item.actor.replace(/_/g, ' ');
                trs += '<tr id="' + item.doc + '" sid="' + item.sid + '" class="db_record"><td class="' + predclass + '">' + item.predicate + '</td><td>' + actor2show + '</td><td>' + item.point + '</td>';
                trs += '<td class="cop" title="' + item.city + '">' + item.cop + '</td><td>' + item.year;
                trs += '</td><td class="rcount">' + item.conf + '</td></tr>';

            });
            trs += "</tbody></table>"
            $('#records_table').html(trs);

            docs_content = '<p /><div class="col-sm-12">';
            docs = response.docs;

            // Display Solr Sentences

            if (tab === 'sen'){
                // count of sentences containing matching propositions
                var totalsentences = response.totalsentences;
                $("#rpanelcount").html(totalsentences + " sentence");
                if (totalsentences > 1 || totalsentences === 0){
                    $("#rpanelcount").append("s")
                }
                // count of sentences matching the solr free-text query
                var formqs = $('#col1-form').serialize();
                // only if no prop-query or a free-text query was entered
                if (formqs.indexOf("actor=&predicate=&point=&") >= 0 ||
                    formqs.indexOf("solrq=") !== formqs.length - "solrq=".length) {
                    $("#rpanelcount").append(
                      "<span style='font-weight:normal;font-style:normal'" +
                      " title='total sentences matching free-text query'>" +
                      " | " +  response.totalsentences_for_solrq + "</span>");
                }

                docs_content += '<table class="table .table-striped" style="margin-top:-15px;"><thead class="blabel">' +
                                '<th>Sentence</th><th class="st">COP</th><th class="st">Year</th></thead><tbody>'
                var ctr = 1;
                $.each(JSON.parse(docs), function (i, item) {
                    var myclass = (item.propidstr !== -1) ? ' class="se2prop"' : '';
                    docs_content += '<tr' + myclass + ' id="' + item.propidstr + '"';
/*                    if (ctr % 2 === 0){
                        docs_content += ' style="background-color:#f0f0f0;"'
                    }*/
                    docs_content += '><td';
                    // css workafound: 1st col of even rows
                    if (ctr %2 !== 0){
                      docs_content += ' class="evsenb"'
                    }
                    docs_content += '>' + item.description + '</td>';
                    docs_content += '<td>' + item.cop + '</td><td';
                    // css workafound: last col of even rows
                    if (ctr %2 !== 0){
                      docs_content += ' class="evsene"'
                    }
                    docs_content += '>' + item.year + '</td></tr>'
                    ctr += 1
                });
            }

            // Display Solr Documents

            else if (tab === 'doc') {
                var totaldocs = response.totaldocs;
                $("#rpanelcount").html(totaldocs + " document");
                if (totaldocs > 1 || totaldocs === 0){
                    $("#rpanelcount").append("s")
                }
                $.each(JSON.parse(docs), function (i, item) {
                    var short_text = item.description.substring(0, 500).split(" ").slice(0, -1).join(" ");
                    // div won't display correctly if short_text ends with <p,
                    if (short_text.match(/<p ?\/?>?$/)) {
                        short_text = short_text.replace(/<p ?\/?>?$/, '');
                    }
                    docs_content += '<div class="result-document"><div class="result-title">' +
                        item.title + '<span class="normaltext" style="float:right;"> [' + item.id +
                        ']</span></div><p />' +
                        //TODO: a "See more" link to see the rest of the document
                        '<div class="result-body">' + short_text + ' ...</div></div>';
                });
            }

            // Display DBpedia entities
            else if (tab === 'dbp'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th><th>Count</th></thead><tbody>'
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td><a class="dbkp" href="' + item.wurl + '" target="_blank">' +
                        item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }

            // Display Reegle thesaurus results
            else if (tab === 'rgl'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th><th>Count</th></thead><tbody>'
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td><a class="dbkp" href="' + item.wurl + '" target="_blank">' +
                        item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }

            // Display keyphrases

            else if (tab === 'kp'){
                docs_content += '<table class="table .table-striped" style="margin-top:-15px;">'
                docs_content += '<thead class="blabel"><th>Label</th><th>Count</th></thead><tbody>'
                $.each(JSON.parse(docs), function (i, item) {
                    docs_content += '<tr class="ek_main" id="' + item.ptmidstr + '">' +
                        '<td>' + item.label +'</td><td>' + item.ecount + '</td></tr>'
                });
            }
            docs_content += "</tbody></table></div>";

            $('#documents').html(docs_content);

            },
            error: function (response) {
            $('#records_table').html("API error 6");

            }
        });
    }


    function get_agree_disagree(){
        $.ajax({
            url: '/ui/agrdis',
            type: 'GET',
            dataType: 'json',
            data: $('#agd-form').serialize(),
            success: function (response) {

            // output string
            var trs = '';

            // data
            entis = response.entis;
            entid = response.entid;
            parsed_entid = JSON.parse(entid);
            rgls = response.rgls;
            rgld = response.rgld;
            parsed_rgld = JSON.parse(rgld);
            kps = response.kps;
            kpd = response.kpd;
            parsed_kpd = JSON.parse(kpd);
            //console.log(entid);
            //console.log(kpd);

            // add key phrases

            var divkp = '';
            var parsed_kps = JSON.parse(kps);
            //console.log("kp length " + parsed_kps.length)
            if (parsed_kps.length < 1){
                divkp = '<div class="col-sm-4" style="text-align:center;">' +
                        '<span class="no_results">' +
                        '<p />No keyphrases</span></div>';
            }
            else {
                divkp = '<div class="col-sm-4" style="overflow-y:auto;height:550px;">' +
                    '<table class="table .table-striped"><thead>' +
                    '<th class="blabel" title="key phrases">KeyPhrase</th>' +
                    '<th class="blabel" style="text-align:right" title="sentences">Count</th>' +
                    '</thead><tbody>';
            }
            trs += divkp;
            $.each(JSON.parse(kps), function (i, item) {
               //console.log("value for key " + item.label + ": " + parsed_kpd[item.label]);
               trs += '<tr class="ke_agd" id="' + parsed_kpd[item.label] + '">' +
                      '<td class="search">' + item.label + '</td><td class="rcount">' +
                      item.ecount + '</td></tr>'
            });
            if (parsed_kps.length > 0){
                trs += "</tbody></table></div>";
            }

            // add dbpedia entities

            var divdbp = '';
            var parsed_entis = JSON.parse(entis);
            //console.log("enti length " + parsed_entis.length)
            if (parsed_entis.length < 1){
                divdbp = '<div class="col-sm-4" style="text-align:center">' +
                         '<span class="no_results">' +
                         '<p />No DBpedia terms</span></div>';
            }
            else {
                divdbp = '<div class="col-sm-4" style="overflow-y:auto;height:550px;">' +
                    '<table class="table .table-striped"><thead>' +
                    '<th class="blabel" title="DBpedia terms">DBpedia</th>' +
                    '<th class="blabel" title="sentences" style="text-align:right">Count</th>' +
                    '</thead><tbody>';
            }
            trs += divdbp;
            $.each(JSON.parse(entis), function (i, item) {
               //console.log("value for key " + item.label + ": " + parsed_entid[item.label]);
               var label2show = item.label.replace(/_/g, ' ')
               trs += '<tr class="en_agd" ' +
                      'id="' + parsed_entid[item.label] + '">' +
                      '<td class="search"><a class="dbkp" href="' + item.wurl +
                      '" target="_blank">' + label2show + '</a></td>' +
                      '<td class="rcount">' + item.ecount + '</td></tr>'
            });
            if (parsed_entis.length > 0){
                trs += "</tbody></table></div>";
            }

            // add reegle terms

            var divrgl = '';
            var parsed_rgl = JSON.parse(rgls);
            //console.log("enti length " + parsed_entis.length)
            if (parsed_rgl.length < 1){
                divrgl = '<div class="col-sm-4" style="text-align:center">' +
                         '<span class="no_results">' +
                         '<p />No ClimTag terms</span></div>';
            }
            else {
                divrgl = '<div class="col-sm-4" style="overflow-y:auto;height:550px;">' +
                    '<table class="table .table-striped"><thead>' +
                    '<th class="blabel" title="Climatetagger API (Reegle Thesaurus terms)">ClimTag</th>' +
                    '<th class="blabel" style="text-align:right" title="sentences">Count</th>' +
                    '</thead><tbody>';
            }
            trs += divrgl;
            $.each(JSON.parse(rgls), function (i, item) {
               //console.log("value for key " + item.label + ": " + parsed_entid[item.label]);
               var label2show = item.label.replace(/_/g, ' ')
               trs += '<tr class="rg_agd" ' +
                      'id="' + parsed_rgld[item.label] + '">' +
                      '<td class="search"><a class="dbkp" href="' + item.wurl +
                      '" target="_blank">' + label2show + '</a></td>' +
                      '<td class="rcount">' + item.ecount + '</td></tr>'
            });
            if (parsed_rgl.length > 0){
                trs += "</tbody></table></div>";
            }

            $('#records_table').html(trs);

            },
            error: function (response) {
            $('#records_table').html("API error 7");

            }
        });
    }

    /*
      Displays single document in right panel 
      Sentence is highlighted (<mark>) if found
     */ 
    function get_solr_doc(id, sid){
        $("#solrdocs").parent("li").addClass("active");
        $("#solrsens").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");

        myurl  = "/ui/solrdoc/"

        $.ajax({
            url: myurl,
            type: 'GET',
            data: {
                doc_id : id,
                sent_id : sid
            },
            dataType: 'json',
            success: function (response) {
                docs_content = '<p /><div class="col-sm-12">';
                $.each(JSON.parse(response), function (i, item) {
                       docs_content += '<div class="result-document">'
                       docs_content += '<div class="result-title">' + item.title
                       docs_content += '<span class="normaltext" style="float:right;"> ['
                       docs_content += item.id + ']</span></div><p />' +
                       //TODO: a "See more" link to see the rest of the document
                       '<div class="result-body">'  + item.description + ' ...</div></div>';
                });
                $('#documents').html(docs_content);

                if($("mark").length){
                    $("mark")[0].scrollIntoView();
                }
                else{
                    $("#solrdocs")[0].scrollIntoView();
                }

            },
            error: function (response) {
                $('#documents').html("API error 8");
            }
         
        });
    }
    
    function get_db_sen(sid){
        $("#solrsens").parent("li").addClass("active");
        $("#solrdocs").parent("li").removeClass("active");
        $("#dbpview").parent("li").removeClass("active");
        $("#rglview").parent("li").removeClass("active");
        $("#kpview").parent("li").removeClass("active");
        var myurl = "/ui/dbsen/";
        $.ajax({
            url: myurl,
            type: 'GET',
            data: {
                sent_id : sid
            },
            dataType: 'json',
            success: function (response) {
                var docs_content = ""
                var trs = ""
                trs += '<table class="table .table-striped" ' +
                            'style="margin-top:-15px;margin-left:10px;padding-right:20px;">' +
                    '<thead><tr><th class="blabel">Sentence</th>' +
                    '<th class="blabel">COP</th><th class="blabel">Year</th></tr>' +
                    '</thead><tbody>'
                trs += '<tr><td>' + response.text + '<span class="sent-id-sm"><p />[' +
                    response.name + ']</span></td>' +
                    '<td class="cop">' + response.cop + '</td>' +
                    '<td>' + response.year + '</td>'
                docs_content += trs
                docs_content += '</tbody></table>'

                $('#documents').html(docs_content);
            },
            error: function (response) {
                $('#documents').html("API error 9");
            }
     });
    }

    function get_sents_for_ek(ids, label){
       var myurl = "/ui/eksent/" + ids + '/' + label + '/';
       $.ajax({
            url: myurl,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
               var docs_content = ""
               var trs = ""
               if (response.length > 0){
                   trs += '<table  class="table .table-striped">' +
                          '<thead><tr><th class="blabel">Sentence</th>' +
                          '<th class="blabel">COP</th><th class="blabel">Year</th></tr>' +
                          '</thead><tbody>'
               }
               $.each(response, function (i, item) {
                   label4re = label.replace("(", "\\(")
                   var labelre = new RegExp("(" + label4re + ")", "gi")
                   var hltext = item.text.replace(labelre, "<span class='blabel'><b>$1</b></span>")
                   trs += '<tr><td>' + hltext + '<span class="sent-id-sm"><p />[' +
                          item.name + ']</span></td>' +
                          '<td class="cop">' + item.cop + '</td>' +
                          '<td>' + item.year + '</td>'
               });
               docs_content += trs
               if (response.length > 0){
                   docs_content += '</tbody></table>'
               }

            $('#documents').html(docs_content);

            },
            error: function (response) {
            $('#documents').html("API error 9");
            }
     });
    }

    // for now, propositions returned by clicking a kp or dbp are not paginable
    function remove_pagers(){
        $("#left-previous").empty();
        $("#left-next").empty();
    }

    function get_props_for_ek(ids, fromtab, sqtohl){
        var myurl = "/ui/ekprop/" + ids + "/" + fromtab + "/";
        //console.log(myurl)

        // add term to highlight to url
        if(sqtohl != undefined){
            myurl += sqtohl + "/";
        }
        console.log(myurl);

        $.ajax({
            //url: param === 'doc' ? '/ui/actors/doc/' : '/ui/actors/dbp',
            url: myurl,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                //console.log("HI2" + JSON.stringify(response))
                var trs = '<table  class="table .table-striped"><thead class="blabel"><tr><th>Actor</th>' +
                          '<th>Action</th><th>Point</th><th>COP</th><th>Year</th>' +
                          '<th title="Confidence">Conf</th></tr></thead><tbody>'
                // make css class for predicate sensitive to predicate type
                $.each(response, function (i, item) {
                    //console.log("ITEM EK2PROP" + item)
                    var predclass = "";
                    if (item.ptype == "support"){
                        predclass = "supp";
                    }
                    else if(item.ptype == "oppose"){
                        predclass = "opp";
                    }
                    else {
                        predclass = "rep";
                    }
                    var actor2show = item.actor.replace(/_/g, ' ');
                    trs += '<tr id="' + item.doc + '" sid="' + item.sid + '" class="db_record"><td>' + actor2show + '</td><td class="' + predclass + '">' + item.predicate + '</td><td>' + item.point + '</td>';
                    trs += '<td class="cop" title="' + item.city + '">' + item.cop + '</td><td>' + item.year + '</td>';
                    trs += '<td class="rcount">' + item.conf + '</td></tr>';
                });
                trs += "</tbody></table>"
                $('#records_table').html(trs);
                setTimeout(remove_pagers(), 3000)
                },
            error: function (response) {
                $('#documents').html("API error 10 (ekprop)");
            }
        });
    }

})
