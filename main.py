
from SMLB.pso_transfer import TPSO
from model.rn50 import Rn50
from model.mbv2 import Mbv2
from model.dn121 import Dn121
from model.swin import Swin_b
from model.vitB import Vit_b
from laser.Vector import Vector
from utils.utils import test_log

rn50 = Rn50()
mbv2 = Mbv2()
dn121 = Dn121()
vitb = Vit_b()
swin_b = Swin_b()

# pt = TPSO(mbv2, Vector)
# pt.setModels([rn50, mbv2, dn121, vitb, swin_b])
# pt.getAdvLB(num_particles=30, max_iterations=100, k=10, S=10, image=Image.open("2.jpg"), inertia_weight=0.9, cognitive_weight=1.6, social_weight=1.8)
