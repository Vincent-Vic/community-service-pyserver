;
var member_index_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $(".wrap_search .search").click(function () {
            $(".wrap_search").submit();
        });
        $(".remove").click(function () {
            that.ops("remove", $(this).attr("data"));
        });
        $(".lock").click(function () {
            that.ops("lock", $(this).attr("data"));
        });
        $(".recover").click(function () {
            that.ops("recover", $(this).attr("data"));
        });
        $(".eye").click(function () {
            that.show($(this).attr("data"));
        });
    },
    show:function (id){
        $.ajax({
            url: common_ops.buildUrl("/order/info"),
            type: "POST",
            data: {
                id: id
            },
            dataType: "json",
            success: function (res) {
                var callback = null;
                if (res.code == 200) {
                    data = res.data
                    content = " <div><ul><li style='display: flex;align-items: center;margin-bottom: 5px;'>" +
                        "<span style='font-weight: bold;font-size: 24px;margin-right: 5px;'>"+data['snap_title'] +"</span>"

                    nature = '互助'
                    nature_color = 'orange'
                    switch (data['snap_nature']) {
                        case 0:
                            nature = '互助'
                            nature_color = 'orange'
                            break;
                        case 1:
                            nature = '服务'
                            nature_color = 'blue'
                            break;
                        case 2:
                            nature = '公益'
                            nature_color = 'green'
                            break;
                    }
                    content = content + " <span class=\"layui-badge layui-bg-"+nature_color+"\">"+nature+"</span></li>"
                    if (data['snap_nature'] === 1){
                         content = content + "<li><span style='font-size: 18px;margin-right: 5px;'>服务费用:</span>"+ data['snap_price'] +"</li>"+
                             "<li><span style='font-size: 18px;margin-right: 5px;'>购买数量:</span>"+ data['pay_num']+"</li>"+
                             "<li><span style='font-size: 18px;margin-right: 5px;'>订单金额:</span>"+ data['price']+"</li>"
                    }

                    content = content +
                        "<li><span style='font-size: 18px;margin-right: 5px;'>提供者昵称:</span> "+data['p_user']['nickname']+"</li>" +
                        "<li><span style='font-size: 18px;margin-right: 5px;'>客户昵称:</span> "+data['c_user']['nickname']+"</li>" +
                        "<li><span style='font-size: 18px;margin-right: 5px;'>客户姓名:</span> "+data['consumer_snap_username']+"</li>" +
                        "<li><span style='font-size: 18px;margin-right: 5px;'>客户电话:</span> "+data['consumer_snap_tel']+"</li>" +
                        "<li><span style='font-size: 18px;margin-right: 5px;'>客户地址:</span> "+
                            data['consumer_snap_province']+data['consumer_snap_city']+
                            data['consumer_snap_county']+data['consumer_snap_description']+
                        "</li>" +
                        "</ul></div>"
                    common_ops.alert(content);
                } else {
                    common_ops.alert(res.msg);
                }

            }
        });

    },
    ops: function (act, id) {
        var callback = {
            "ok": function () {
                $.ajax({
                    url: common_ops.buildUrl("/service/ops"),
                    type: "POST",
                    data: {
                        act: act,
                        id: id
                    },
                    dataType: "json",
                    success: function (res) {
                        var callback = null;
                        if (res.code == 200) {
                            callback = function () {
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert(res.msg, callback);
                    },
                    error:common_ops.errorHandle
                });
            },
            "cancel": null
        };
        var tip = ''
        switch (act) {
            case 'remove':
                tip = '确定删除？'
                break
            case 'recover':
                tip = '确定恢复？'
                break
            case 'lock':
                tip = '确定冻结？'
                break
        }
        common_ops.confirm(tip, callback);
    }
};

$(document).ready(function () {
    member_index_ops.init();
});