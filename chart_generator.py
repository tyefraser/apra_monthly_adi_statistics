import pandas as pd
import plotly.express as px
import plotly as pt
import altair as alt
import plotly.graph_objects as go

def chart_selected_col_bar(
        df,
        category_column,
        reference_col,
        title = None,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
        xaxis_title=None,
        yaxis_title=None,
):
    # Validate input DataFrame columns
    if category_column not in df.columns or reference_col not in df.columns:
        raise ValueError(f"Columns {category_column} or {reference_col} not found in DataFrame.")

    # Default category order
    if ordered_category_list is None:
        ordered_category_list = df[category_column].tolist()

    # Handle color mapping
    if color_discrete_map is None:
        color_discrete_map = {}
    color_discrete_map.setdefault('default_color', '#83C9FF')

    # Ensure text column exists
    text_column = f"{reference_col} - text"
    if text_column not in df.columns:
        df[text_column] = ''

    # Create the bar chart
    fig = px.bar(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=title,
        color=category_column,
        text=df[text_column],
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=[color_discrete_map.get('default_color', '#83C9FF')],
        height=800
    )

    # Format x-axis
    if x_tickformat:
        fig.update_xaxes(tickformat=x_tickformat) # ".0%" for no decimal places

    if x_gridcolor:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=x_gridcolor)

    if xaxis_title is None:
        xaxis_title=reference_col

    if yaxis_title is None:
        yaxis_title=category_column
    
    # Layout customization
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        legend_title=category_column,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=False,
    )

    if not show_xaxis_labels:
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])
    
    
    # fig.update_layout(
    #     autosize=True,
    # )
    ## fig.update_layout(
    ##     xaxis=dict(
    ##         domain=[0.35, 0.95]  # Adjust the start and end points as needed
    ##     )
    ## )
    ## fig.update_layout(margin_pad=10)
    ## fig.update_yaxes(
    ##     scaleanchor="x",
    ##     scaleratio=1,
    ## )
    ## fig.update_xaxes(
    ##     constraintoward='right'  # This moves the plot area to make space for text
    ## )

    return fig


def chart_selected_col_line(
        df,
        category_column,
        reference_col,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
):
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
        color_discrete_map = {'default_color': '#83C9FF'}

    # Plot with Plotly Express
    fig = px.line(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=f"{reference_col}",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=[color_discrete_map['default_color']],
        height=800
    )

    # Format the x-axis
    if x_tickformat != None:
        fig.update_xaxes(tickformat=x_tickformat)  # ".0%" for no decimal places
        # fig.update_xaxes(tickformat=x_tickformat, tickmode='linear')  # ".0%" for no decimal places

    if x_gridcolor != None:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=x_gridcolor)

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=reference_col,
        yaxis_title=category_column,
        legend_title=category_column,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=False,
    )

    if not show_xaxis_labels:
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])

    return fig