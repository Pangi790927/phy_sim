import glm

# aabb - stands for axis aligned bounded box? where aa is the left-bottom corner
#        and bb is the right-top corner
# para - stands for a general paralepiped, O is the bottom-left corner, N is
#        an upwards pointing arrow from O to the top-left corner and M is an
#        arrow pointing to the bottom-right corner 

# obs1: all those functions return a list of glm.vec or None if no intersection
# obs2: there may be duplicated points inside the result
# obs3: on coincident shapes you get only some points, diffrent per case
# obs4: those only test if the shape's perimeters intersect
# obs5: point_* returns the point back on intersection as a single element list

# set this variable to true if you want to make aabb functions correct corners
_AABB_FIX = True

# on coincident: 4 directions: C1 + glm.vec(+/-1, +/-1)
def circle_circle(C1, r1, C2, r2):
    return glm_circ_circ(glm.vec2(C1), float(r1), glm.vec2(C2), float(r2))

def segment_circle(A, B, center, radius):
    return glm_seg_circ(glm.vec2(A), glm.vec2(B), glm.vec2(center),
            float(radius))

# on coincident: the overlap interval
def segment_segment(A1, B1, A2, B2):
    return glm_seg_seg(glm.vec2(A1), glm.vec2(B1), glm.vec2(A2), glm.vec2(B2))

def point_circle(P, C, radius):
    return glm_p_circ(glm.vec2(P), glm.vec2(C), float(radius))

def point_aabb(P, AA, BB):
    return glm_p_aabb(glm.vec2(P), glm.vec2(AA), glm.vec2(BB))

def point_parallelogram(P, O, N, M):
    return glm_p_para(glm.vec2(P), glm.vec2(O), glm.vec2(N), glm.vec2(M))

def point_triangle(P, E, F, G):
    return glm_p_tri(glm.vec2(P), glm.vec2(E), glm.vec2(F), glm.vec2(G))

def aabb_circle(AA, BB, C, radius):
    return glm_aabb_circ(glm.vec2(AA), glm.vec2(BB), glm.vec2(C), float(radius))

def aabb_segment(AA, BB, A, B):
    return glm_aabb_seg(glm.vec2(AA), glm.vec2(BB), glm.vec2(A), glm.vec2(B))

def aabb_aabb(AA1, BB1, AA2, BB2):
    return glm_aabb_aabb(glm.vec2(AA1), glm.vec2(BB1), glm.vec2(AA2),
            glm.vec2(BB2))

def circle_parallelogram(C, radius, O, N, M):
    return glm_circ_para(glm.vec2(C), float(radius),
            glm.vec2(O), glm.vec2(N), glm.vec2(M))

def segment_parallelogram(A, B, O, N, M):
    return glm_seg_para(glm.vec2(A), glm.vec2(B),
            glm.vec2(O), glm.vec2(N), glm.vec2(M))

def aabb_parallelogram(AA, BB, O, N, M):
    return glm_aabb_para(glm.vec2(AA), glm.vec2(BB),
            glm.vec2(O), glm.vec2(N), glm.vec2(M))

def parallelogram_parallelogram(O1, N1, M1, O2, N2, M2):
    return glm_para_para(glm.vec2(O1), glm.vec2(N1), glm.vec2(M1),
            glm.vec2(O2), glm.vec2(N2), glm.vec2(M2))

def circle_triangle(C, radius, E, F, G):
    return glm_circ_tri(glm.vec2(C), float(radius),
            glm.vec2(E), glm.vec2(F), glm.vec2(G))

def segment_triangle(A, B, E, F, G):
    return glm_seg_tri(glm.vec2(A), glm.vec2(B),
            glm.vec2(E), glm.vec2(F), glm.vec2(G))

def aabb_triangle(AA, BB, E, F, G):
    return glm_aabb_tri(glm.vec2(AA), glm.vec2(BB),
            glm.vec2(E), glm.vec2(F), glm.vec2(G))

def parallelogram_triangle(O, N, M, E, F, G):
    return glm_para_tri(glm.vec2(O), glm.vec2(N), glm.vec2(M),
            glm.vec2(E), glm.vec2(F), glm.vec2(G))

def triangle_triangle(E1, F1, G1, E2, F2, G2):
    return glm_tri_tri(glm.vec2(E1), glm.vec2(F1), glm.vec2(G1),
            glm.vec2(E2), glm.vec2(F2), glm.vec2(G2))

# implementation using glm.vec for points:
# ==============================================================================

_2D_UP = glm.vec2(0, 1)
_2D_DOWN = glm.vec2(0, -1)
_2D_LEFT = glm.vec2(-1, 0)
_2D_RIGHT = glm.vec2(1, 0)

def _aabb_fix(AA, BB):
    A = glm.vec2(min(AA.x, BB.x), min(AA.y, BB.y))
    B = glm.vec2(max(AA.x, BB.x), max(AA.y, BB.y))
    return A, B

def _get_aabb_segs(AA, BB):
    AB = glm.vec2(BB.x, AA.y)
    BA = glm.vec2(AA.x, BB.y)
    return [(AA, AB), (AB, BB), (BB, BA), (BA, AA)]

def _get_para_segs(O, N, M):
    return [(O, O + N), (O + N, O + N + M), (O + N + M, O + M), (O + M, O)]

def _get_tri_segs(E, F, G):
    return [(E, F), (F, G), (G, E)]

def _tri_sign(P, A, B):
    s = P - B
    u = P - A
    return s.x * u.y - u.x * s.y

def _segs_intersect(segs, int_fn):
    ret_ints = []
    for a, b in segs:
        ints = int_fn(a, b)
        if ints:
            for i in ints:
                ret_ints.append(i)
    if len(ret_ints) == 0:
        return None
    return ret_ints

# https://stackoverflow.com/questions/3349125/
#       circle-circle-intersection-points
def glm_circ_circ(C1, r1, C2, r2):
    ret_intersect = []
    if C1 == C2 and r1 == r2:
        return [C1 + _2D_UP * r1, C1 + _2D_DOWN * r1,
                C1 + _2D_LEFT * r1, C1 + _2D_RIGHT * r1]
    d2 = glm.length2(C1 - C2)
    if d2 > (r1 + r2) ** 2:
        return None
    if d2 < abs(r1 - r2) ** 2:
        # circle inside circle
        return None
    # else we can intersect them
    d = d2 ** 0.5
    a = (r1 ** 2 - r2 ** 2 + d2) / (2 * d)
    h = (r1 ** 2 - a ** 2) ** 0.5
    C = C1 + a * (C2 - C1) / d
    return [
        glm.vec2(C.x + h * (C2.y - C1.y) / d, C.y - h * (C2.x - C1.x) / d),
        glm.vec2(C.x - h * (C2.y - C1.y) / d, C.y + h * (C2.x - C1.x) / d)
    ]

# https://codereview.stackexchange.com/questions/86421
#       /line-segment-to-circle-collision-algorithm
def glm_seg_circ(A, B, Q, rad):
    ret_intersect = []
    V = B - A
    a = glm.dot(V, V)
    b = 2 * glm.dot(V, A - Q)
    c = glm.dot(A, A) + glm.dot(Q, Q) - 2 * glm.dot(A, Q) - rad**2
    disc = b**2 - 4*a*c
    if disc < 0:
        return None
    t1 = (-b + disc ** 0.5) / (2 * a)
    t2 = (-b - disc ** 0.5) / (2 * a)
    if 0 <= t1 <= 1:
        ret_intersect.append(A + V * t1)
    if 0 <= t2 <= 1:
        ret_intersect.append(A + V * t2)
    if len(ret_intersect) == 0:
        return None
    return ret_intersect

# https://stackoverflow.com/questions/563198/
#       how-do-you-detect-where-two-line-segments-intersect
# answ 2 for the reference
def glm_seg_seg(A1, B1, A2, B2):
    S1 = B1 - A1
    S2 = B2 - A2
    det = (-S2.x * S1.y + S1.x * S2.y)
    s1 = (-S1.y * (A1.x - A2.x) + S1.x * (A1.y - A2.y))
    t1 = ( S2.x * (A1.y - A2.y) - S2.y * (A1.x - A2.x))
    if det == 0:
        if t1 == 0:
            # colinearity case
            a0 = glm.dot((A2 - A1), S2) / glm.dot(S2, S2)
            a1 = a0 + glm.dot(S1, S2) / glm.dot(S2, S2)
            aux = a0
            a0 = min(a0, a1)
            a1 = max(aux, a1)
            if a1 >= 0 and a0 <= 1:
                a0 = max(0, a0)
                a1 = min(1, a1)
                return [A1 + a0 * S1, A1 + a1 * S1]
            # colinear but non-overlapping
            return None
        # paralel
        return None
    s = s1 / det
    t = t1 / det
    if 0 <= s <= 1 and 0 <= t <= 1:
        return [A1 + t * S1]
    return None

def glm_p_circ(P, C, r):
    if glm.length2(P - C) < r * r:
        return [P]
    return None

def glm_p_aabb(P, AA, BB):
    if _AABB_FIX:
        AA, BB = _aabb_fix(AA, BB)
    if AA.x <= P.x <= BB.x and AA.y <= P.y <= BB.y:
        return [P]
    return None

def glm_p_para(P, O, N, M):
    if glm_p_tri(P, O, O + N, O + M):
        return [P]
    if glm_p_tri(P, O + N + M, O + N, O + M):
        return [P]
    return None

# https://stackoverflow.com/questions/2049582/
#       how-to-determine-if-a-point-is-in-a-2d-triangle
def glm_p_tri(P, E, F, G):
    d1 = _tri_sign(P, E, F)
    d2 = _tri_sign(P, F, G)
    d3 = _tri_sign(P, G, E)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    if not (has_pos and has_neg):
        return [P]
    return None

# Bellow you can find unoptimized intersection functions:

def glm_aabb_circ(AA, BB, C, r):
    if _AABB_FIX:
        AA, BB = _aabb_fix(AA, BB)
    aabb_segs = _get_aabb_segs(AA, BB)
    def _seg_circ_local(a, b):
        return glm_seg_circ(a, b, C, r)
    return _segs_intersect(aabb_segs, _seg_circ_local)

def glm_aabb_seg(AA, BB, A, B):
    if _AABB_FIX:
        AA, BB = _aabb_fix(AA, BB)
    aabb_segs = _get_aabb_segs(AA, BB)
    def _seg_seg_local(a, b):
        return glm_seg_seg(a, b, A, B)
    return _segs_intersect(aabb_segs, _seg_seg_local)

def glm_aabb_aabb(AA1, BB1, AA2, BB2):
    if _AABB_FIX:
        AA1, BB1 = _aabb_fix(AA1, BB1)
        AA2, BB2 = _aabb_fix(AA2, BB2)
    aabb_segs1 = _get_aabb_segs(AA1, BB1)
    aabb_segs2 = _get_aabb_segs(AA2, BB2)
    def _seg_aabb_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(aabb_segs2, _seg_seg_local)
    return _segs_intersect(aabb_segs1, _seg_aabb_local)

def glm_circ_para(C, r, O, N, M):
    para_segs = _get_para_segs(O, N, M)
    def _seg_circ_local(a, b):
        return glm_seg_circ(a, b, C, r)
    return _segs_intersect(para_segs, _seg_circ_local)

def glm_seg_para(A, B, O, N, M):
    para_segs = _get_para_segs(O, N, M)
    def _seg_circ_local(a, b):
        return glm_seg_seg(a, b, A, B)
    return _segs_intersect(para_segs, _seg_circ_local)

def glm_aabb_para(AA, BB, O, N, M):
    if _AABB_FIX:
        AA, BB = _aabb_fix(AA, BB)
    aabb_segs1 = _get_aabb_segs(AA, BB)
    para_segs2 = _get_para_segs(O, N, M)
    def _seg_para_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(para_segs2, _seg_seg_local)
    return _segs_intersect(aabb_segs1, _seg_para_local)

def glm_para_para(O1, N1, M1, O2, N2, M2):
    para_segs1 = _get_para_segs(O1, N1, M1)
    para_segs2 = _get_para_segs(O2, N2, M2)
    def _seg_para_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(para_segs2, _seg_seg_local)
    return _segs_intersect(para_segs1, _seg_para_local)

def glm_circ_tri(C, r, E, F, G):
    tri_segs = _get_tri_segs(E, F, G)
    def _seg_circ_local(a, b):
        return glm_seg_circ(a, b, C, r)
    return _segs_intersect(tri_segs, _seg_circ_local)

def glm_seg_tri(A, B, E, F, G):
    tri_segs = _get_tri_segs(E, F, G)
    def _seg_seg_local(a, b):
        return glm_seg_seg(a, b, A, B)
    return _segs_intersect(tri_segs, _seg_seg_local)

def glm_aabb_tri(AA, BB, E, F, G):
    if _AABB_FIX:
        AA, BB = _aabb_fix(AA, BB)
    aabb_segs1 = _get_aabb_segs(AA, BB)
    tri_segs2 = _get_tri_segs(E, F, G)
    def _seg_tri_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(tri_segs2, _seg_seg_local)
    return _segs_intersect(aabb_segs1, _seg_tri_local)

def glm_para_tri(O, N, M, E, F, G):
    para_segs1 = _get_para_segs(O, N, M)
    tri_segs2 = _get_tri_segs(E, F, G)
    def _seg_tri_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(tri_segs2, _seg_seg_local)
    return _segs_intersect(para_segs1, _seg_tri_local)

def glm_tri_tri(E1, F1, G1, E2, F2, G2):
    tri_segs1 = _get_tri_segs(E1, F1, G1)
    tri_segs2 = _get_tri_segs(E2, F2, G2)
    def _seg_tri_local(a, b):
        def _seg_seg_local(c, d):
            return glm_seg_seg(a, b, c, d)
        return _segs_intersect(tri_segs2, _seg_seg_local)
    return _segs_intersect(tri_segs2, _seg_tri_local)
