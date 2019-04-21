from pyscipopt import Model
import pytest
import os

# This test requires a directory link in tests/ to check/ in the main SCIP directory.

testset = []
primalsolutions = {}
dualsolutions = {}
tolerance = 1e-5
infinity = 1e20

#testsetpath = 'check/testset/short.test'
#solufilepath = 'check/testset/short.solu'

#testsetpath = '/home/tkeady5/Documents/scipoptsuite-6.0.1/scip/check/testset/short.test'
#solufilepath = '/home/tkeady5/Documents/scipoptsuite-6.0.1/scip/check/testset/short.solu'

testsetpath = 'check/testset/one.test'
solufilepath = 'check/testset/one.solu'

print("******** After path declarations ********")


class MyBranching(Branchrule):

    def __init__(self, model, cont):
        self.model = model
        self.cont = cont
        self.count = 0
        self.was_called_val = False
        self.was_called_int = False

    def branchexeclp(self, allowaddcons):
        self.model.getLPBranchCands()
        self.count += 1
        if self.count >= 2:
            return {"result": SCIP_RESULT.DIDNOTRUN}
        assert allowaddcons

        assert not self.model.inRepropagation()
        assert not self.model.inProbing()
        self.model.startProbing()
        assert not self.model.isObjChangedProbing()
        self.model.fixVarProbing(self.cont, 2.0)
        self.model.constructLP()
        self.model.solveProbingLP()
        self.model.getLPObjVal()
        self.model.endProbing()

        self.integral = self.model.getLPBranchCands()[0][0]

        if self.count == 1:
            down, eq, up = self.model.branchVarVal(self.cont, 1.3)
            self.model.chgVarLbNode(down, self.cont, -1.5)
            self.model.chgVarUbNode(up, self.cont, 3.0)
            self.was_called_val = True
            down2, eq2, up2 = self.model.branchVar(self.integral)
            self.was_called_int = True
            self.model.createChild(6, 7)
            return {"result": SCIP_RESULT.BRANCHED}



if not all(os.path.isfile(fn) for fn in [testsetpath, solufilepath]):
    if pytest.__version__ < "3.0.0":
        pytest.skip("Files for testset `short` not found (symlink missing?)")
    else:
        pytestmark = pytest.mark.skip
        print("******** Pytest version good ********")

else:
    with open(testsetpath, 'r') as f:
        for line in f.readlines():
            testset.append('check/' + line.rstrip('\n'))
        print("******** Done reading lines form testsetpath ********")

    with open(solufilepath, 'r') as f:
        for line in f.readlines():

            if len(line.split()) == 2:
                [s, name] = line.split()
            else:
                [s, name, value] = line.split()

            if   s == '=opt=':
                primalsolutions[name] = float(value)
                dualsolutions[name] = float(value)
            elif s == '=inf=':
                primalsolutions[name] = infinity
                dualsolutions[name] = infinity
            elif s == '=best=':
                primalsolutions[name] = float(value)
            elif s == '=best dual=':
                dualsolutions[name] = float(value)
            # status =unkn= needs no data
        print("******** Done reading lines from solufilepath ********")


def relGE(v1, v2, tol = tolerance):
    print("******** Inside relGE ********")
    if v1 is None or v2 is None:
        return True
    else:
        reltol = tol * max(abs(v1), abs(v2), 1.0)
        return (v1 - v2) >= -reltol

def relLE(v1, v2, tol = tolerance):
    print("******** Inside relLE ********")
    if v1 is None or v2 is None:
        return True
    else:
        reltol = tol * max(abs(v1), abs(v2), 1.0)
        return (v1 - v2) <= reltol

def setup_function(function):
    print("setting up %s" % function)


@pytest.mark.parametrize('instance', testset)
def test_instance(instance):
    print("******** Inside test_instance ********")
    print(instance)    
    s = Model()
    s.hideOutput()
    s.readProblem(instance)

    # Copy pasta from test_branch_probin_lp
    my_branchrule = MyBranching(s)
    m.includeBranchrule(my_branchrule, "test branch", "test branching and probing and lp functions",
                    priority=10000000, maxdepth=3, maxbounddist=1)


    s.optimize()

    print("******** Done optimizing ********")

    name = os.path.split(instance)[1]
    if name.rsplit('.',1)[1].lower() == 'gz':
        name = name.rsplit('.',2)[0]
    else:
        name = name.rsplit('.',1)[0]

    # we do not need the solution status
    primalbound = s.getObjVal()
    dualbound = s.getDualbound()

    # get solution data from solu file
    primalsolu = primalsolutions.get(name, None)
    dualsolu = dualsolutions.get(name, None)

    print("******** Before asserts ********")

    if s.getObjectiveSense() == 'minimize':
        print("******** 'minimize' ********")
        assert relGE(primalbound, dualsolu)
        assert relLE(dualbound, primalsolu)
    else:
        print("******** not 'minimize' ********")
        if( primalsolu == infinity ): primalsolu = -infinity
        if( dualsolu == infinity ): dualsolu = -infinity
        assert relLE(primalbound, dualsolu)
        assert relGE(dualbound, primalsolu)
