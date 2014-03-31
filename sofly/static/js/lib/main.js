$(function() {
    
    var flights, request, doSearch;

    var delay = (function() {
        var timer = 0;
        return function(callback, ms) {
            clearTimeout (timer);
            timer = setTimeout(callback, ms);
        };
    })();

    var today = new Date(),
        dd = today.getDate(),
        mm = today.getMonth()+1,
        yyyy = today.getFullYear();
    
    if(dd<10){dd='0'+dd} if(mm<10){mm='0'+mm} var dt = mm+dd+yyyy;
    
    var $departDate = $('#search_one input[name="DepartureDate1"]'),
        $returnDate = $('#search_one input[name="ReturnDate"]')
        $departDateMulti = $('#search_multi input[name^="DepartureDate"]');

    $departDateMulti.datepicker({
            onRender: function(date) {
                return date.valueOf() < today.valueOf() ? 'disabled' : '';
            }
        }).on('changeDate', function(ev) {
            $('.datepicker').hide();
        }).data('datepicker');

    var departDate = $departDate.datepicker({
            onRender: function(date) {
                return date.valueOf() < today.valueOf() ? 'disabled' : '';
            }
        }).on('changeDate', function(ev) {
            if (ev.date.valueOf() > returnDate.date.valueOf()) {
                var newDate = new Date(ev.date)
                newDate.setDate(newDate.getDate());
                returnDate.setValue(newDate);
            }
            departDate.hide();
            $returnDate[0].focus();
        }).data('datepicker');        

    var returnDate = $returnDate.datepicker({
            onRender: function(date) {
                return date.valueOf() <= departDate.date.valueOf() ? 'disabled' : '';
            }
        }).on('changeDate', function(ev) {
            returnDate.hide();
        }).data('datepicker');

    $('.trip-type').on('change', 'input', function() {
        var name = $(this).attr('name');
        
        if (name == 'IsOneWay') {
            $('input[name="ReturnDate"]').attr('disabled', 'disabled').closest('.form-group').hide();
        } else {
            $('input[name="ReturnDate"]').removeAttr('disabled').closest('.form-group').show();
        }

        if (name =='IsMultiCity') {         
            $('#search_one').addClass('hidden');
            $('#search_multi').removeClass('hidden');
        } else {
            $('#search_one').removeClass('hidden');
            $('#search_multi').addClass('hidden');   
        }

        $('#search .search-form:hidden input').each(function() {
            if ($(this).prop('required'))
                $(this).removeProp('required').addClass('required');
        });       

        $('#search .search-form:visible input').each(function() {
            if ($(this).hasClass('required'))
                $(this).prop('required',true);
        });               
    });

    $('.airport-code')
        .on('mouseover',function() {
            var $this = $(this);
            //$this.unbind('hover');
            $.get(SCRIPT_ROOT + '/search/airport/'+$this.data('value'), function(data) {
                var json = $.parseJSON(data);
                $this.popover({content: json.name, 'placement': 'top'}).popover('show');
            });
        })
        .on('mouseout',function() {
            $(this).popover('hide');
        })        

    // searching
    $('#flight_lookup, #ticket_lookup').on('submit', function() {
        $(this).find('input[type="submit"]').button('loading');
        $('#search .search-form.hidden input').each(function() {
            this.disabled = true;
        });        
        $('.progress').removeClass('hidden');
        return true;
    });

    $('.trip-type').on('change', 'input', function() {
        setTimeout(function() {
            $('.trip-type input').each(function() {
                this.value = $(this).closest('label').hasClass('active');
            });
        }, 50);
    })

    // search for airport
    $('.airports')
        .on('keyup', function() {
            if (!doSearch) return;
            var $this = $(this),
                $results = $this.closest('.airports-wrapper').find('.airports-results'),
                input = this.value;
            delay(function() {
                if (request) request.abort();
                request = $.getJSON('/search/airports', {q:input}, function(data) {
                    var html = makeList(data);
                    $results.empty().html(html);
                    if ($results.find('.list-group').length && $this.is(':focus'))
                        $results.show();
                });    
            }, 10);
        })
        .on('blur', function(e) {   
            $('.airports-results').hide();
        })
        .on('focus click', function() {
            var $results = $(this).closest('.airports-wrapper').find('.airports-results');
            if ($results.find('.list-group').length)
                $results.show();
        }); 

    $('.airports-results').on('mousedown', 'a', function(e) {
        var $parent = $(this).closest('.airports-wrapper');
        $parent.find('.airports').val($(this).text());
        $parent.find('.airports-results').hide();
        return false;
    });  

    // tooltips
    $('body').tooltip({selector: "[data-toggle=tooltip]",});
    /*$('#results table tr').popover({
        'html':true,
        'placement':'right',
        'trigger':'hover'
    });*/                               
    
    // some key bindings
    $(document)
        .on('keydown', function(e){
            var $results = $('.airports-results'),
                visible = $results.is(':visible');
            doSearch = false;
            if (e.keyCode === 38) { // up
               console.log('up');
               return;
            }
            else if (e.keyCode === 40) { // down
                if (visible) {
                    console.log('down');   
                }
                return;
            }
            else if (e.keyCode == 27 || e.keyCode == 9) { // esc or tab
                doSearch = false;
                $results.hide();
                return;
            // control characters 
            } else if ($.inArray(e.keyCode,[8,9,13,16,17,18,19,20,27,33,34,35,36,37,38,39,40,45,46,91,93,112,123,144,145]) > 0) 
                return;
            doSearch = true;    
        });

    // catch 403 forbiddens
    $(document).ajaxError(function(event, request, settings) {
        if (request.status === 401)
            $('#login-modal').modal('show');
        else if (request.status === 403)
            console.log('unverified');
    });

    // fade-in
    function fadeIn() {
        $('.fade-in').animate({
            opacity: 1
        },0);
    }
    window.setTimeout(fadeIn, 10);   

    // alerts fade-in
    function showAlert() {
        $('.alert').addClass('in');
    }
    window.setTimeout(showAlert, 100);         

});

function makeList(list) {
    var html = '<div class="list-group">';
    (function subList(item) {
        $.each(item, function() {
            if (!$.isEmptyObject(this.S)) {
                subList(this.S);                
                return; 
            }
            html += '<a href="#" class="list-group-item">' + this.N + '</a>';
        });
    })(list);
    html += '</div>';        
    return html;
}

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}  