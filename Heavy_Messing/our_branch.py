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
        cdef int bestcand
        cdef SCIP_Real* bestdown = <SCIP_Real*> malloc(sizeof(SCIP_Real))
        cdef SCIP_Real* bestup = <SCIP_Real*> malloc(sizeof(SCIP_Real))
        cdef SCIP_Real* bestscore = <SCIP_Real*> malloc(sizeof(SCIP_Real))
        cdef SCIP_Bool* bestdownvalid = <SCIP_Bool*> malloc(sizeof(SCIP_Bool))
        cdef SCIP_Bool* bestupvalid = <SCIP_Bool*> malloc(sizeof(SCIP_Bool))
        cdef SCIP_Real* provedbound = <SCIP_Real*> malloc(sizeof(SCIP_Real))
        cedf SCIP_RESULT* result = <SCIP_RESULT*> malloc(sizeof(SCIP_RESULT))

        #no skipping, no limit to prop rounds, no probing bounds, yes forcestrongbranch
        PY_SCIP_CALL(SCIPselectVarStrongBranching(self.model, &lpcands, &lpcandssol, &lpcandsfrac, False, False, nlpcands, npriolpcands, nlpcands, 0, -1, False, True, &bestcand, &bestdown, &bestup, &bestscore, &bestdownvalid, &bestupvalid, &provedbound, &result)

        _,_,_ = self.model.branchVar(bestcand)
        return {"result": SCIP_RESULT.BRANCHED}
