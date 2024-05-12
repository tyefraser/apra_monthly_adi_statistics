import streamlit as st

def write_variable(
        var_type,
        variable,
):
    if var_type == 'plot':
        st.plotly_chart(variable, use_container_width=True)

def generate_4_tabs(
        tab_dict,
        tab_dict_list,
):
    
    tab_1, tab_2, tab_3, tab_4 = st.tabs(tab_dict_list)

    with tab_1:
        list_of_lists=tab_dict[tab_dict_list[0]]
        for list in list_of_lists:
            write_variable(
                var_type=list[0],
                variable=list[1],
            )
    with tab_2:
        list_of_lists=tab_dict[tab_dict_list[1]]
        for list in list_of_lists:
            write_variable(
                var_type=list[0],
                variable=list[1],
            )
    with tab_3:
        list_of_lists=tab_dict[tab_dict_list[2]]
        for list in list_of_lists:
            write_variable(
                var_type=list[0],
                variable=list[1],
            )
    with tab_4:
        list_of_lists=tab_dict[tab_dict_list[3]]
        for list in list_of_lists:
            write_variable(
                var_type=list[0],
                variable=list[1],
            )


def generate_tabs(
        tab_dict
):
    tab_dict_list = list(tab_dict.keys())

    if len(tab_dict_list) == 4:
        generate_4_tabs(
            tab_dict=tab_dict,
            tab_dict_list=tab_dict_list,
        )