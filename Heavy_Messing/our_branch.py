from cpython cimport Py_INCREF, Py_DECREF
from libc.stdlib cimport malloc, free
from libc.stdio cimport fdopen
from pyscipopt import Model, Branchrule, SCIP_RESULT, quicksum

class Our_Branch_Rule(Branchrule):

    def __init__(self, model):
        self.model = model

    def branchexeclp(self):
        self.model.startProbing()
        self.model.constructLP()
        self.model.solveProbingLP()
        self.model.getLPObjVal()
        self.model.endProbing()

        lpcands, lpcandssol, lpcandsfrac, nlpcands, npriolpcands, nfracimplvars = self.model.getLPBranchCands()

        #no skipping, no limit to prop rounds, no probing bounds, yes forcestrongbranch
        bestcand = self.model.selectVarStrongBranch(lpcands, lpcandssol, lpcandsfrac, nlpcands, npriolpcands)

        _,_,_ = self.model.branchVar(bestcand)
        return {"result": SCIP_RESULT.BRANCHED}
