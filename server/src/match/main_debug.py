#%%
import numpy as np
import utils as ut
from importlib import reload
ut = reload(ut)
UtilsRender = ut.UtilsRender
from game_entities import CapFactory, Arrow

#%%
w = 1920
h = 1080
X = np.array(
    [[  30,  540],
    [1280,  540]]
)

cap_factory = CapFactory(X=X)
arrow = Arrow(
    caps=cap_factory,
    cap_index=0,
    arrow_length=100,
    angle=0
)

#%%