$('#results table tbody').on('click only-result', 'tr', function(event) {

    var $this = $(this),
        by_price = $('#results table').hasClass('by-price');
        
    $this.toggleClass('selected').siblings('tr').removeClass('selected');

    var $table = $('.table-selection'),
        $selected = $table.find('tr.selected'),
        completed = $selected.length==$table.length
        total = 0;

        var $summary = $('#itinerary');
        $summary.find('tbody').html($selected.clone(true))
        $summary.find('td.hidden, th.hidden').removeClass('hidden');
        $summary.find('.hide-in-summary').addClass('hidden');

    if (by_price) {
        var num = parseInt($this.closest('.tab-pane').data('number')) + 1,
            data = $this.data(),
            table = ID_TABLE
            ids = [];

        // traverse table and create array of ids
        $selected.each(function() { table = table[$(this).data('identifier')] });
        for (var key in table) { ids.push(key) }

        // toggle available flight options
        $('#results_'+ num +' tbody tr').each(function() {
            if ($.inArray($(this).data('identifier'), ids) === -1)
                $(this).hide();
            else
                $(this).show();
        });            

        // update price when all selected
        if (completed  && ('price' in table)) 
            total = table.price;


    } else {
        $selected.each(function() {
            total += parseFloat($(this).data('price'));
        });
        total = total.toFixed(2)
    }

    if (completed)
        $('#results').data('price', total).find('.total-price').html(total);
    
    selectTab($this, completed, (event.type=='only-result') ? 0 : 200);
});

// watch fare
$('#results').on('click', '.watch-fare', function() {
        var $this = $(this);

        // get ids
        var id = [];
        $('.table-selection tr.selected').each(function() {
            id.push($(this).data('identifier'));
        });

        var d = $('#results').data(),
            data = {
                code      : d.code,
                id        : id.join('|'),
                name      : d.name,                   
                paid      : d.paid || d.price,
                price     : d.price,
                search    : d.search
            }

        console.log(data);
        $this.button('loading');

        $.post('/results/watch', data)
            .always(function(resp) {
                $this.attr('disabled','disabled');
            })
            .done(function(response) {
                $('<i />', { class: 'glyphicon glyphicon-ok left-buffer'})
                    .appendTo($this.text(toTitleCase(response.status)));
            })
            .fail(function(xhr, textStatus, errorThrown) {
                console.log(xhr);
                $('<i />', { class: 'glyphicon glyphicon-remove left-buffer'})
                    .appendTo($this.addClass('btn-danger')
                        .text(toTitleCase($.parseJSON(xhr.responseText).status)));
            });
    });

/* 
    tab and pane selection 
*/
function selectTab($row, completed, timeout) {
    var $curPane = $row.closest('.tab-pane'),
        $curTab = $('a[href="#'+ $curPane.attr('id') +'"]'),
        $lastTab = $('#results .nav-pills li:last');     

    // last tab disabling
    if (completed){$lastTab.removeClass('disabled');}else{$lastTab.addClass('disabled');}

    if ($('#results table').hasClass('by-price')) {

    }
    
    if ($row.hasClass('selected')) {
        setTimeout(function() {
            $curTab.closest('li').addClass('disabled').find('i.glyphicon-ok-circle').removeClass('invisible');
            $('a[href="#'+ $curPane.next().attr('id') +'"]').tab('show');
        }, timeout);
    } else {
        $curTab.closest('li').removeClass('disabled').find('i.glyphicon-ok-circle').addClass('invisible');
    }
} 