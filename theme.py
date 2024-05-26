import plotly.io as pio
import plotly.graph_objects as go

# Define custom colors
gray = 'rgb(193,188,188)'
purple = 'rgb(120,3,150)'
blue = 'rgb(184,216,220)'
grey_dark = 'rgb(91,85,85)' 
light_purple = 'rgb(180, 150, 200)' 
turquoise = 'rgb(64, 224, 208)'
gold = 'rgb(214,194,146)'
brown = 'rgb(150,29,33)'
midnight_blue = 'rgb(25, 25, 112)'
blue_dark = 'rgb(60,116,123)'
purple_light = 'rgb(210,154,243)'
gold_dark = 'rgb(128,101,39)'
black = 'rgb(0,0,0)'
deep_gold = 'rgb(176, 145, 50)'
dark_grey = 'rgb(77, 77, 77)'
olive_green = 'rgb(128, 128, 0)'
soft_blue = 'rgb(150, 190, 220)'
rich_brown = 'rgb(139, 69, 19)'
slate_blue = 'rgb(106, 90, 205)'



# Color
colors = [gray,purple, gold, brown, blue, blue_dark, grey_dark, purple_light, gold_dark, black,
                      light_purple, deep_gold, dark_grey, olive_green, soft_blue, rich_brown, slate_blue, turquoise, midnight_blue]


pio.templates["myname"] = go.layout.Template(layout=go.Layout(colorway=colors))

# Define the custom template with grid lines
pio.templates["Neoma_template"] = go.layout.Template(
    layout=go.Layout(
        legend_title_text='',
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis=dict(
            showgrid=True,     # Enable the Y-axis grid
            gridcolor='lightgrey',  # Set the grid color
            gridwidth=1        # Set the grid width
        )
    )
)

# Set the default template
theme = "plotly+Neoma_template+myname"