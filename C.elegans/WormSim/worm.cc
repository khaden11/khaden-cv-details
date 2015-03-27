/* 
This software is freely available for use in research, teaching and other
non-commercial purposes.  Users have the right to modify, alter, improve,
or enhance the software without limitation, under the condition that you
do not remove or alter the copyright information in this section.

If you publish results which were obtained using the software, or its
source code, please cite the software with a reference to the associated 
publication:

J.H. Boyle, S. Berri and N. Cohen (2012), Gait modulation in C. elegans:
an integrated neuromechanical model, Front. Comput. Neurosci, 6:10 
doi: 10.3389/fncom.2012.00010

Licence information for Sundials IDA can be found in "sundials-2.3.0/LICENCE"
*/

// Required includes
#include <iostream>
#include <cmath>
#include <fstream>
#include <cstdlib>

#include <ida/ida.h>
#include <ida/ida_dense.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>
#include <sundials/sundials_math.h>

#include <string>
//#include "DESolver.h"
//#include "DESolver.cpp"

#include <sstream>
#include <cctype>

using namespace std;

// Simulation paramaters				
#define DURATION  5				//duration of simulation (in seconds)
#define MEDIUM 1.0				//change in the range 0.0 (water) to 1.0 (agar)
#define OBJECTS 0				//set number of objects (>= 0)
#define LAYOUT 0				//change between 0 (square) 1 (hex) 2 (random)

// Simulator constants
#define NSEG 48
#define NBAR NSEG+1
#define NSEG_MINUS_1 NSEG-1
#define NEQ   3*(NBAR)
#define DELTAT 0.001
#define HALFPI M_PI/2.0

// General body constants
realtype D = 80e-6;
realtype R[NBAR];
realtype L_seg = 1e-3/NSEG;

// Horizontal element constants
realtype k_PE = (NSEG/24.0)*RCONST(10.0e-3);  	
realtype D_PE = RCONST(0.025)*k_PE;		
realtype AE_PE_ratio = RCONST(20.0);    
realtype k_AE = AE_PE_ratio*k_PE;
realtype D_AE = RCONST(5.0)*AE_PE_ratio*D_PE;	

// Diagonal element constants
realtype k_DE = RCONST(350.0)*k_PE;	
realtype D_DE = RCONST(0.01)*k_DE;	

// Length constant holders
realtype L0_P[NSEG];
realtype L_min[NSEG] ;
realtype L0_P_minus_L_min[NSEG];
realtype L0_D[NSEG];

// Stretch receptor constant holders
realtype SR_shape_compensation[NSEG];

// Muscle time constant
realtype T_muscle = RCONST(0.1);	

// Environment constants
realtype CL_water = RCONST(3.3e-6/(2.0*NBAR));
realtype CN_water = RCONST(5.2e-6/(2.0*NBAR));
realtype CL_agar = RCONST(3.2e-3/(2.0*NBAR));
realtype CN_agar = RCONST(128e-3/(2.0*NBAR));

// Environment variables
realtype K_agar = CN_agar/CL_agar;
realtype CN[NBAR];
realtype CL[NBAR];
realtype ContactForce;
int N_objects = OBJECTS;
int root_N = round(sqrt(N_objects));
realtype Objects[OBJECTS][3];
realtype k_Object = k_PE*5;

// Communication variables  
realtype L_SR[NSEG][2];
realtype I_SR[NSEG][2];

// Neuron and muscle state variables
realtype V_muscle[NSEG][2];
realtype V_neuron[NSEG][2];

// Declare output file
ofstream outfile;

// Prototypes of functions called by IDA (Copied from Sundials examples)

//EDITED FUNCTIONS FOR DE
int run_wormsim(string outputfile, float NMJWEIGHT, float SRWEIGHT, float IONV, float IOND, float BILINEAR);
void update_neurons(realtype timenow, float NMJWEIGHT, float IONV, float IOND);
void update_SR(realtype timenow, float BILINEAR);
double rnd_num(double minValue,double maxValue);

double func(double *X, double *Xl, double *Xu);

double distance_travelled(string filename);
void printgeninfo(double distance, double gennumber, double *params);


void update_external(realtype timenow);
int resrob(realtype tres, N_Vector yy, N_Vector yp, N_Vector resval, void *rdata);

void update_muscles(realtype timenow);

static int grob(realtype t, N_Vector yy, N_Vector yp, realtype *gout, void *g_data);

// Prototypes of private functions (Copied from Sundials examples)
static void SaveOutput(void *mem, realtype t, N_Vector y);
static void PrintFinalStats(void *mem);
static int check_flag(void *flagvalue, char *funcname, int opt);
double randn(double mu, double sigma);

/*
 *--------------------------------------------------------------------
 * Main Program
 *--------------------------------------------------------------------
 */

int main(void)
{
   //##########################################################
   //#######     IMPLEMENTATION OF DE ALGORITHM      ##########
   //##########################################################   
   
   //DEFINE MAIN CONSTANTS USED IN ALGORITHM
   #define MAX_GEN 50 
   #define N_POP 10
   #define N_PARAM 5
   //#define F_WEIGHT 0.8
   #define C_CONST 0.9
   
   /* Random number generator defined by URAND should return
   double-precision floating-point values uniformly distributed
   over the interval [0.0, 1.0)					*/
   #define URAND drand48()
   
   /* Definition for random number generator initialization	*/
   #define INITRAND srand48(time(0))
   
   //INITIALISE VARIABLES
   int count, jrand, a, b, c = 0;
  
   //NMJ WEIGHT, SR WEIGHT, IONV, IOND, BILINEARV
   double Xl[N_PARAM] = {-10,-10,0,0,-10}; //UPPER AND LOWER 
   double Xu[N_PARAM] = {10,10,10,10,10};      //BOUNDS FOR PARAMETERS
   double popul[N_POP][N_PARAM]; //CREATE VECTOR FOR ALL POPULATIONS
   double prevdist[N_POP];
   double trial[N_PARAM]; //CREATE TRIAL VECTOR TO COMPARE AGAINST CURRENT POPULATION
   
   double populnext[N_POP][N_PARAM];
   
   //double furthestdist = 0;
   double furthestdist = 0; //USE IF ALREADY RUN BEFORE WITH VALUES
   
   double bestparams[N_PARAM] = {0,0,0,0,0};
   
   long hz;
   /* Resolve clock frequency of a computer and initialize random
      number generator	 */

   hz = sysconf(_SC_CLK_TCK);
   INITRAND;
   
   
   //INITIALISE VECTORS IN CURRENT POPULATIONS WITH RANDOM NUMBERS BETWEEN PARAMETER CONSTRAINTS
   for (int i = 0; i < N_POP; i++) {
      for (int j = 0; j < N_PARAM; j++) {
         popul[i][j] = Xl[j] + (Xu[j] - Xl[j])*URAND;
      }
   }
   
   /*//IF ALREADY RUN ALGORITHM - USE PREVIOUSLY DETERMINED BEST VALUES IF WANTED
   for (int i = 0; i < N_POP; i++) {
      popul[i][0] = 1.50572;
      popul[i][1] = 0.990764;
      popul[i][2] = 0.2;
      popul[i][3] = 1.73674;
      popul[i][4] = 2.20049;
   }*/
   
   //MAIN LOOP
   while (count < MAX_GEN){  //RUN THROUGH MAX NUMBER OF GENERATIONS
      double F_WEIGHT = URAND;
      while (F_WEIGHT < 0.5) {
         F_WEIGHT = URAND;
      }
          
      for(int k = 0; k < N_POP; k++){  //RUN THROUGH ALL POPULATIONS OF PARAMETERS
         
         double currdist = 0;
         
         if(popul[k][N_PARAM] != populnext[k][N_PARAM]) {
            run_wormsim("currpop", popul[k][0], popul[k][1], popul[k][2], popul[k][3], popul[k][4]);//RUN WORMSIM ON CURRENT POPULATION
            currdist, prevdist[k] = distance_travelled("currpop.csv");//CALCULATE THE DISTANCE TRAVELLED BY THE WORM
         }
         
         if(popul[k][N_PARAM] == populnext[k][N_PARAM]) {
            currdist = prevdist[k];
         }
         
         
         if(currdist > furthestdist) { //IF THIS IS THE FURTHEST DISTANCE, MAKE A RECORD OF IT
            furthestdist = currdist;
            for(int i = 0; i < N_PARAM; i++) {
               bestparams[i] = popul[k][i];
            }
         }

         //CREATE THREE RANDOM VARIABLES USED FOR MUTATING VALUES IN RANDOM POPULATIONS
         do {
            a = URAND*N_POP;
         }
         while (a==k);
         
         do {
            b = URAND*N_POP;
         }
         while (b==k || b==a);
         
         do {
            c = URAND*N_POP; 
         }
         while (c==k || c==a || c==b);

         //FOR MUTATION AND CROSSOVER
         jrand = URAND*N_PARAM; //CREATE NUMBER FOR RANDOM PARAMETER
         
         for (int l = 0; l < N_PARAM; l++){  //LOOP THROUGH PARAMETERS OF PARTICULAR POPULATION                           
            if (URAND < C_CONST || l == jrand){ 
               trial[l]= popul[c][l] + F_WEIGHT*(popul[a][l] - popul[b][l]);  //MUTATE PARAMETER BY USING RANDOM VARIABLES AND THE F WEIGHTING CONSTANT
            }          
            else {
            trial[l]= popul[k][l]; //ELSE KEEP THE PARAMETER THE SAME
            }
         }
         
         trial[N_PARAM] = func(trial, Xl, Xu); //MAKE SURE THERE ARE NO PARAMETERS OUTSIDE THE CONSTRAINTS
                                                                 //IF SO, CORRECT THEM         
                                                                 
         run_wormsim("trialpop", trial[0], trial[1], trial[2], trial[3], trial[4]); //RUN WORMSIM ON THE NEWLY MUTATED TRIAL ARRAY
         double trialdist = distance_travelled("trialpop.csv"); //FIND DISTANCE WORM TRAVELS IN THE TRIAL RUN
         
         if(trialdist > furthestdist) { //IF THIS IS THE FURTHEST DISTANCE, MAKE A RECORD OF IT
            furthestdist = trialdist;
            for(int i = 0; i < N_PARAM; i++) {
               bestparams[i] = trial[i];
            }
         }
         
         if (trialdist > currdist) {
            for(int m = 0; m < N_PARAM; m++) {
               populnext[k][m] = trial[m];
            }
         }
         if (trialdist <= currdist) {
            for(int n = 0; n < N_PARAM; n++) {
               populnext[k][n] = popul[k][n];
            }
         }
         
         for(int o = 0; o < N_POP; o++) {
            for (int p = 0; p < N_PARAM; p++) {
               popul[o][p] = populnext[o][p];
            }
         }
      }
      printgeninfo(furthestdist, (count + 1), bestparams); //PRINT INFO FOR BEST PARAMETERS IN CURRENT GENERATION
      count ++;
   }
   
   run_wormsim("bestpop", bestparams[0], bestparams[1], bestparams[2], bestparams[3], bestparams[4]);//RUN WORMSIM ON BEST POPULATION TO GET MATLAB DATA FILE   
   
   return 1;
}
/*
 *--------------------------------------------------------------------
 * Model Functions
 *--------------------------------------------------------------------*/

void printgeninfo(double distance, double gennumber, double *params) {
   
   cout << "Generation : " << gennumber << endl;
   cout << "Distance travelled : " << distance << endl;
   cout << "Parameters used : ";
   for (int i = 0; i < 5; i++) {
      cout << params[i] << " ";
   }
   cout << "\n" << endl;
}


double func(double *X, double *Xl, double *Xu){
/* Correction of boundary constraint violations, violating variable
   values are reflected back from the violated boundary        */

   for (int i = 0; i < N_PARAM; i++)
   {
        if (X[i] < Xl[i]) {
           X[i] = 2.0*Xl[i] - X[i];
        }
        if (X[i] > Xu[i]) {
           X[i] = 2.0*Xu[i] - X[i];
        }
   }

   return *X;
}

double distance_travelled(string filename) {

         int maxlines = 0;
         ifstream file(filename.c_str());
         string line;
         string woo;
         
         while(getline(file, line)) {
            ++maxlines;
         }
         file.close();
         
         int w = 0;
         ifstream lastline(filename.c_str());
         string lline;
         string coordx;
         string coordy;
         while(getline(lastline, woo)) {
            w = w+1;
            if(w == maxlines) {
               lline = woo;
            }
         }
         
         stringstream stream(lline);
         string x;
         string y;
         string skip;
         
         stream >> skip;
         stream >> x;
         stream >> y;
         

         string xword = x.substr(0,x.length()-1);
         string yword = y.substr(0,y.length()-1);
         double xcor;
         double ycor;
         
         stringstream convert(xword);
         convert >> xcor;
         
         stringstream converty(yword);
         converty >> ycor;
               
         double distance = (xcor*xcor)/* + (ycor*ycor)*/;  
         return distance;
}

/* 
 * MAIN RUNNING FUNCTION FOR ALGORITHM*/
 
 
  int run_wormsim(string outputfile, float NMJWEIGHT, float SRWEIGHT, float IONV, float IOND, float BILINEAR){
          // IDA variables (Copied from Sundials examples)
          void *mem;
          N_Vector yy, yp, avtol;
          realtype rtol, *yval, *ypval, *atval;
          realtype t0, tout, tret;
          int iout, retval, retvalr;  

          mem = NULL;
          yy = yp = avtol = NULL;
          yval = ypval = atval = NULL;

          // Allocate N-vectors (Copied from Sundials examples)
          yy = N_VNew_Serial(NEQ);
          if(check_flag((void *)yy, "N_VNew_Serial", 0)) return(1);
          yp = N_VNew_Serial(NEQ);
          if(check_flag((void *)yp, "N_VNew_Serial", 0)) return(1);
          avtol = N_VNew_Serial(NEQ);
          if(check_flag((void *)avtol, "N_VNew_Serial", 0)) return(1);

          // Create and initialize  y, y', and absolute tolerance vectors (Copied from Sundials examples)
          yval  = NV_DATA_S(yy);
          ypval = NV_DATA_S(yp);  
          rtol = (MEDIUM < 0.015 ? 0.1 : 1)*RCONST(1.0e-12);
          atval = NV_DATA_S(avtol);

          
          for(int i = 0; i < NBAR; ++i){
	        // Initialize body in straight line
	        yval[i*3] = i*L_seg;
	        yval[i*3+1] = RCONST(0.0);
	        yval[i*3+2] = M_PI/RCONST(2.0);

	        // Initialize derivative values (Copied from Sundials examples)
         	ypval[i*3] = RCONST(0.0);
          	ypval[i*3+1] = RCONST(0.0);
          	ypval[i*3+2] = RCONST(0.0);

	        // Set absolute tolerances for solver (Copied from Sundials examples)
	        // Tolerance must be set lower when simulating in water, due to lower drag coefficients
	        atval[i*3] = (MEDIUM < 0.015 ? 0.1 : 1)*RCONST(1.0e-9);
	        atval[i*3+1] = (MEDIUM < 0.015 ? 0.1 : 1)*RCONST(1.0e-9);
	        atval[i*3+2] = (MEDIUM < 0.015 ? 0.1 : 1)*RCONST(1.0e-5);

          }
          
          // Initialize model variables
          for(int i = 0; i < NSEG; ++i){
	        V_muscle[i][0] = 0.0;
	        V_muscle[i][1] = 0.0;
	        V_neuron[i][0] = 0.0;
	        V_neuron[i][1] = 0.0;
	        I_SR[i][0] = 0.0;
	        I_SR[i][1] = 0.0;
          }  
          
          // Set local body radius values based on elliptical approximation
          for(int i = 0; i < NBAR; ++i){	
	        R[i] = D/2.0*fabs(sin(acos((i-NSEG/2.0)/(NSEG/2.0 + 0.2))));		
          } 

          // Set stretch receptor weightings that compensate for the elliptical shape,
          // giving approximately the same SR response to segment mending angle
          for(int i = 0; i < NSEG; ++i){
	        SR_shape_compensation[i] = (D/(R[i] + R[i+1])*SRWEIGHT);  //MULTIPLY BY PARAMETER FOR SRWEIGHT
          } 
         
          // Set muscle constants (rest length, minimum length etc) accounting 
          // for length differences due to the elliptical body shape
          for(int i = 0; i < NSEG; ++i){
	        float scale = 0.65*((R[i] + R[i+1])/D);
	        L0_P[i] = sqrt(pow(L_seg,2) + pow((R[i] - R[i+1]),2));
	        L_min[i] = (1.0-scale)*L0_P[i];
	        L0_P_minus_L_min[i] = L0_P[i] - L_min[i];
	        L0_D[i] = sqrt(pow(L_seg,2) + pow((R[i] + R[i+1]),2));
          }

          // Set drag constants according to medium
          for(int i = 0; i < NBAR; ++i){
          	CL[i] = (CL_agar - CL_water)*MEDIUM + CL_water;
          	CN[i] = (CN_agar - CN_water)*MEDIUM + CN_water;
          }

          // Integration start time 
          t0 = RCONST(0.0);
          
          // Call IDACreate and IDAMalloc to initialize IDA memory (Copied from Sundials examples)
          mem = IDACreate();
          if(check_flag((void *)mem, "IDACreate", 0)) return(1);

          retval = IDAMalloc(mem, resrob, t0, yy, yp, IDA_SV, rtol, avtol);	
          if(check_flag(&retval, "IDAMalloc", 1)) return(1);
          
          realtype hmax = RCONST(10000.0);
          IDASetMaxStep(mem, hmax);
          
          // Free avtol (Copied from Sundials examples) 
          N_VDestroy_Serial(avtol);

          // Call IDADense and set up the linear solver (Copied from Sundials examples) 
          retval = IDADense(mem, NEQ);
          if(check_flag(&retval, "IDADense", 1)) return(1);

          // Open output file  //ALTER OUTPUT FILENAME
          string fileend = ".csv";
          string file;
          
          file = outputfile + fileend;
          
          outfile.open(file.c_str());  
          
          // Integrator inputs
          iout = 0; 
          tout = DELTAT;

          // Save current state
          SaveOutput(mem,0,yy);
          
          
          //CREATE DIRECTION VARIABLES
          
          double initialx, initialy, finalx, finaly;
          
          

          // Loop through model for specified amount of time
          while(1) {
           
            	// Call residual function (Copied from Sundials examples)
	        // to update physical model (Sundials takes multiple steps)
            	retval = IDASolve(mem, tout, &tret, yy, yp, IDA_NORMAL);    	
            
            	// Call stretch receptor update function
            	update_SR(tout, BILINEAR);

            	// Call neural model update function
            	update_neurons(tout, NMJWEIGHT, IONV, IOND);

            	//Call muscle model update function
            	update_muscles(tout);

            	// Save current state
            	SaveOutput(mem,tret,yy);

	        // Check integration went ok (Copied from Sundials examples) 
            	if(check_flag(&retval, "IDASolve", 1)) return(1);
                
	        // Prepare to go to next step
            	if (retval == IDA_SUCCESS) {
              		iout++;
              		tout += DELTAT;
            	}
                   
	        // End once enough simulation time has passed
            	if (tout > DURATION) break;
          }

          // (Copied from Sundials examples) 
          //PrintFinalStats(mem);

          // Free memory (Copied from Sundials examples) 
          IDAFree(&mem);
          N_VDestroy_Serial(yy);
          N_VDestroy_Serial(yp);

          // Close output file
          outfile.close();
          
        }

 
 
  // Neural circuit function
  void update_neurons(realtype timenow, float NMJWEIGHT, float IONV, float IOND){

   	// Neural paramaters
   	const int N_units = 12;		// Number of neural units
   	const float Hyst = 0.5;		// Neural hysteresis - originally 0.5
   	const float I_on = 0.675;       // AVB input current (makes the model go) -- 0.675
   	// GJ coupling strength
   	float I_coupling = 0.0;		// Optional gap junction coupling between adjacent neurons (has virtually no effect, not usually used)

   	// Set up neuromuscular junctions   
   	float NMJ_weight[NSEG];
   	for(int i = 0; i < NSEG; ++i){
   	        NMJ_weight[i] =  0.7*(1.0 - i * 0.6/NSEG)*NMJWEIGHT;  //MULTIPLY BY PARAMETER NMJWEIGHT
   	        
		//NMJ_weight[i] =  0.7*(1.0 - i * 0.6/NSEG); default	// Decreasing gradient in NMJ strength / muscle efficacy
   	}
   	//NMJ_weight[0] /= 1.5; DEFAULT VALUE
   	NMJ_weight[0] /= 1.5;				// Helps to prevent excessive bending of head

   	// Neural state variables
   	static int State[N_units][2]; 

	// If this is the first time update_neurons is called, initialize with all neurons on one side ON
   	static bool initialized = false;
   	if(!initialized){
		for(int i = 0; i < N_units; ++i){
			State[i][0] = 1;
			State[i][1] = 0;
		}
		initialized = true;
   	}   

   	// Stretch receptor variables   	
   	float I_SR_D[N_units];
   	float I_SR_V[N_units];
   	float SR_weight[N_units];

   	int N_SR = 6;	//This refers to the number of UNITS (not segments) that each unit receives feedback from (thus 1 means just local feedback)   
   	int N_seg_per_unit = (int)(NSEG/N_units);   

   	// SR_weight is a global weighting for each unit, used to get the compensate for curvature gradient induced by the NMJ gradient above
   	for(int i = 0; i < N_units; ++i){	
		//SR_weight[i] = 0.65*(0.4 + 0.08*i)*(N_units/12.0)*(2.0/N_seg_per_unit);
		SR_weight[i] = 0.65*(0.4 + 0.08*i)*(N_units/12.0)*(2.0/N_seg_per_unit);
   	}

   	/*// Get SR input   
   	for(int i = N_units - 1 ; i >= (N_units - N_SR - 1); --i){ 	// Posterior part of worm (i.e., units whose stretch receptors are full length)
		I_SR_D[i] = 0.0;
		I_SR_V[i] = 0.0;
		for(int j = 0; j < N_SR; ++j){	// Contributions from each of N_SR consecutive units (each containing 2 segments)
			I_SR_D[i] += I_SR[(i-j)*N_seg_per_unit][0] + (N_seg_per_unit >= 2)*I_SR[(i-j)*N_seg_per_unit + 1][0] + (N_seg_per_unit >= 3)*I_SR[(i-j)*N_seg_per_unit + 2][0]  + (N_seg_per_unit >= 4)*I_SR[(i-j)*N_seg_per_unit + 3][0];	
			I_SR_V[i] += I_SR[(i-j)*N_seg_per_unit][1] + (N_seg_per_unit >= 2)*I_SR[(i-j)*N_seg_per_unit + 1][1] + (N_seg_per_unit >= 3)*I_SR[(i-j)*N_seg_per_unit + 2][1]  + (N_seg_per_unit >= 4)*I_SR[(i-j)*N_seg_per_unit + 3][1];	
		}		
   	}
   	int tmp_N_SR = N_SR;
   	for(int i = (N_units - N_SR - 2); i >= 0; --i){		// Posterior part of worm, with stretch receptors terminating at tail
		tmp_N_SR --;		// Count one unit less
		I_SR_D[i] = 0.0;
		I_SR_V[i] = 0.0;
		for(int j = 0; j < tmp_N_SR; ++j){	// Contributions are not weighted at this point
			I_SR_D[i] += I_SR[(i-j)*N_seg_per_unit][0] + (N_seg_per_unit >= 2)*I_SR[(i-j)*N_seg_per_unit + 1][0] + (N_seg_per_unit >= 3)*I_SR[(i-j)*N_seg_per_unit + 2][0]  + (N_seg_per_unit >= 4)*I_SR[(i-j)*N_seg_per_unit + 3][0];	
			I_SR_V[i] += I_SR[(i-j)*N_seg_per_unit][1] + (N_seg_per_unit >= 2)*I_SR[(i-j)*N_seg_per_unit + 1][1] + (N_seg_per_unit >= 3)*I_SR[(i-j)*N_seg_per_unit + 2][1]  + (N_seg_per_unit >= 4)*I_SR[(i-j)*N_seg_per_unit + 3][1];	
		}			
   	}	*/

// ORIGINAL STRETCH RECEPTOR CONTRIBUTIONS

   	// Add up stretch receptor contributions from all body segments in receptive field for each neural unit 
   	for(int i = 0; i <= N_units - N_SR; ++i){
		I_SR_D[i] = 0.0;
		I_SR_V[i] = 0.0;
		for(int j = 0; j < N_SR; ++j){
			I_SR_D[i] += I_SR[(i+j)*N_seg_per_unit][0] + (N_seg_per_unit >= 2)*I_SR[(i+j)*N_seg_per_unit + 1][0] + (N_seg_per_unit >= 3)*I_SR[(i+j)*N_seg_per_unit + 2][0]  + (N_seg_per_unit >= 4)*I_SR[(i+j)*N_seg_per_unit + 3][0];	
			I_SR_V[i] += I_SR[(i+j)*N_seg_per_unit][1] + (N_seg_per_unit >= 2)*I_SR[(i+j)*N_seg_per_unit + 1][1] + (N_seg_per_unit >= 3)*I_SR[(i+j)*N_seg_per_unit + 2][1]  + (N_seg_per_unit >= 4)*I_SR[(i+j)*N_seg_per_unit + 3][1];				
		}		
   	}
	
	// For units near the tail, fewer segments contribute (because the body ends)
   	int tmp_N_SR = N_SR;
   	for(int i = (N_units - N_SR + 1); i < N_units; ++i){			
		tmp_N_SR --;
		I_SR_D[i] = 0.0;
		I_SR_V[i] = 0.0;
		for(int j = 0; j < tmp_N_SR; ++j){
			I_SR_D[i] += I_SR[(i+j)*N_seg_per_unit][0] + (N_seg_per_unit >= 2)*I_SR[(i+j)*N_seg_per_unit + 1][0] + (N_seg_per_unit >= 3)*I_SR[(i+j)*N_seg_per_unit + 2][0]  + (N_seg_per_unit >= 4)*I_SR[(i+j)*N_seg_per_unit + 3][0];	
			I_SR_V[i] += I_SR[(i+j)*N_seg_per_unit][1] + (N_seg_per_unit >= 2)*I_SR[(i+j)*N_seg_per_unit + 1][1] + (N_seg_per_unit >= 3)*I_SR[(i+j)*N_seg_per_unit + 2][1]  + (N_seg_per_unit >= 4)*I_SR[(i+j)*N_seg_per_unit + 3][1];
		}			
   	}	

   	/*for(int i = 0; i <= (N_units - N_SR - 2); ++i){ 
		//COMPENSATE ANTERIORLY
		I_SR_D[i] *= sqrt(N_SR / ((i + 1.)));
		I_SR_V[i] *= sqrt(N_SR / ((i + 1.)));
   	}*/
   	
   	
   	// Compensate for the posterior segments with shorter processes   	
   	for(int i = (N_units - N_SR + 1); i < N_units; ++i){ 
		I_SR_D[i] *= sqrt(-(N_SR/(i-N_units)));
		I_SR_V[i] *= sqrt(-(N_SR/(i-N_units))); //-POSTERIOR COMPENSATION
	}

   	// Variables for total input current to each B-class motorneuron
   	float I_D[N_units];
   	float I_V[N_units];

   	// Current bias to compensate for the fact that neural inhibition only goes one way
   	float I_bias = 0.5; //default value 0.5

	// Combine AVB current, stretch receptor current, neural inhibition and bias
   	for(int i = 0; i < N_units; ++i){
   	        
		I_D[i] = I_on + SR_weight[i]*I_SR_D[i]*IOND;
		I_V[i] = (I_bias - State[i][0]) + I_on + SR_weight[i]*I_SR_V[i]*IONV; //MULTIPLY BY ALTERED IONV AND D PARAMETERS

   	}

   	// Add gap junction currents if they are being used (typically I_coupling = 0)
   	I_D[0] += (State[1][0] - State[0][0])*I_coupling;
   	I_V[0] += (State[1][1] - State[0][1])*I_coupling;

   	for(int i = 1; i < N_units-1; ++i){
		I_D[i] += ((State[i+1][0] - State[i][0]) + (State[i-1][0] - State[i][0]))*I_coupling;
		I_V[i] += ((State[i+1][1] - State[i][1]) + (State[i-1][1] - State[i][1]))*I_coupling;
	}

   	I_D[N_units-1] += (State[N_units-2][0] - State[N_units-1][0])*I_coupling;
   	I_V[N_units-1] += (State[N_units-2][1] - State[N_units-1][1])*I_coupling;
   

   	// Update state for each bistable B-class neuron
   	for(int i = 0; i < N_units; ++i){
   		if(I_D[i] > (0.5 + Hyst/2.0 - Hyst*State[i][0])){
			State[i][0] = 1;}
  		else{
			State[i][0] = 0;}

   		if(I_V[i] > (0.5 + Hyst/2.0 - Hyst*State[i][1])){
			State[i][1] = 1;}
   		else{
			State[i][1] = 0;}   
		//cout << "D : " << I_D[i] << " " << (0.5 + Hyst/2.0 - Hyst*State[i][0]) << "  V : " << I_V[i] << " " << (0.5 + Hyst/2.0 - Hyst*State[i][1]) << endl;
   	}
   	//cout << I_D[1] << " " << (0.5 + Hyst/2.0 - Hyst*State[1][0]) << " " << I_V[1] << " " << (0.5 + Hyst/2.0 - Hyst*State[1][1]) << endl;        

   	// Compute effective input to each muscle including B-class excitation and contralateral D-class inhibition  	
   	for(int i = 0; i < NSEG; ++i){		
		V_neuron[i][0] = NMJ_weight[i]*State[(int)(i*N_units/NSEG)][0] - NMJ_weight[i]*State[(int)(i*N_units/NSEG)][1];
		V_neuron[i][1] = NMJ_weight[i]*State[(int)(i*N_units/NSEG)][1] - NMJ_weight[i]*State[(int)(i*N_units/NSEG)][0];	
   	}   
  }

  // Update the stretch receptors (for each segment). These
  // are weighted and combined as input to the neural units in function "update_neurons"
  void update_SR(realtype timenow, float BILINEAR){
   	for(int i = 0; i < NSEG; ++i){	
		// Bilinear SR function on one side to compensate for asymmetry and help worm go straight
		I_SR[i][0] = SR_shape_compensation[i]*((L_SR[i][0] - L0_P[i])/L0_P[i]*((L_SR[i][0] > L_seg) ? 0.8:1.2))*BILINEAR; //MULTIPLY BY BILINEAR PARAMETER
		I_SR[i][1] = SR_shape_compensation[i]*((L_SR[i][1] - L0_P[i])/L0_P[i]);
   	}
  }

  // Update the simple muscle "model" (electronic)
  void update_muscles(realtype timenow){
  	//Muscle transfer function is just a simple LPF
  	for(int i = 0; i < NSEG; ++i){
		for(int j = 0; j < 2; ++j){
			realtype dV = (V_neuron[i][j] - V_muscle[i][j])/T_muscle;
			V_muscle[i][j] += dV*DELTAT;		
		}
  	}
  }

  // System residual function which implements physical model (Based on Sundials examples) 
  int resrob(realtype tres, N_Vector yy, N_Vector yp, N_Vector rr, void *rdata)
  {
  	// Import data from vectors
  	realtype *yval, *ypval, *rval;
  	yval = NV_DATA_S(yy); 
  	ypval = NV_DATA_S(yp); 
  	rval = NV_DATA_S(rr);  

  	//Declare variables
  	realtype CoM[NBAR][3];
  	realtype V_CoM[NBAR][3];
  	realtype term[NBAR][2][2];  		// Nseg, d/v, x/y
  	realtype V_term[NBAR][2][2];
  	realtype dy,dx,dVy,dVx,F_even,F_odd;
  	realtype F_term[NBAR][2][2];
  	realtype F_term_rotated[NBAR][2][2];
  	realtype V_CoM_rotated[NBAR][3];

  	realtype L[NSEG][2];				// Nseg, d/v
  	realtype Dir[NSEG][2][2];			// Nseg, d/v, x/y
  	realtype S[NSEG][2];
  	realtype L_D[NSEG][2];			// Nseg, \,/   <- these are the angles of the diagonals
  	realtype Dir_D[NSEG][2][2];  			// Nseg, \,/ , x/y
  	realtype S_D[NSEG][2];

  	realtype L0_AE, T, F_AE, F_PE, F_PD;
  	realtype F_H[NSEG][2];  
  	realtype F_D[NSEG][2];

  	realtype L_EXT;
  	realtype F_EXT[2];

  	realtype F_object[NBAR][2][2];
	// Initialize all object forces to zero incase objects are not being used
	for(int i = 0; i < NBAR; ++i){
		for(int j = 0; j < 2; ++j){
			for(int k = 0; k < 2; ++k){
				F_object[i][j][k] = 0;
			}
		}
	}
  	
  	for(int i = 0; i < NBAR; ++i){
		// Extract CoM of each solid rod from vectors
		int three_i = i*3;	
		CoM[i][0] = yval[three_i];
		CoM[i][1] = yval[three_i + 1];
		CoM[i][2] = yval[three_i + 2];

		// Calculate positions of D/V points based on CoM, angle and radius
		dx = R[i]*cos(CoM[i][2]);
		dy = R[i]*sin(CoM[i][2]);

		term[i][0][0] = CoM[i][0] + dx;
		term[i][0][1] = CoM[i][1] + dy;
		term[i][1][0] = CoM[i][0] - dx;
		term[i][1][1] = CoM[i][1] - dy;

		// Extract CoM velocities of each solid rod from vectors
		V_CoM[i][0] = ypval[three_i];
		V_CoM[i][1] = ypval[three_i + 1];
		V_CoM[i][2] = ypval[three_i + 2];

		// Calculate velocity of D/V points based on CoM velocity, rate of rotation and radius
		realtype V_arm = R[i]*V_CoM[i][2];		
		dVx = V_arm*cos(CoM[i][2] + HALFPI);  		
		dVy = V_arm*sin(CoM[i][2] + HALFPI);  		

		V_term[i][0][0] = V_CoM[i][0] + dVx;
		V_term[i][0][1] = V_CoM[i][1] + dVy;
		V_term[i][1][0] = V_CoM[i][0] - dVx;
		V_term[i][1][1] = V_CoM[i][1] - dVy;		
  	}	

  
  	// Get Horizontal/Diagonal element lengths and lengthening/shortening velocities
  	for(int i = 0; i < NSEG; ++i){

		// Strange format for efficiency
		int iplus1 = i+1;
	
		Dir[i][0][0] = (term[iplus1][0][0] - term[i][0][0]);
		Dir[i][0][1] = (term[iplus1][0][1] - term[i][0][1]);
		L[i][0] = sqrt(pow(Dir[i][0][0],2.0) + pow(Dir[i][0][1],2.0));
		Dir[i][0][0] /= L[i][0];
		Dir[i][0][1] /= L[i][0];
		S[i][0] = (V_term[iplus1][0][0] - V_term[i][0][0])*Dir[i][0][0] + (V_term[iplus1][0][1] - V_term[i][0][1])*Dir[i][0][1];

		Dir[i][1][0] =  (term[iplus1][1][0] - term[i][1][0]);
		Dir[i][1][1] =  (term[iplus1][1][1] - term[i][1][1]);
		L[i][1] = sqrt(pow(Dir[i][1][0],2.0) + pow(Dir[i][1][1],2.0));
		Dir[i][1][0] /= L[i][1];
		Dir[i][1][1] /= L[i][1];
		S[i][1] = (V_term[iplus1][1][0] - V_term[i][1][0])*Dir[i][1][0] + (V_term[iplus1][1][1] - V_term[i][1][1])*Dir[i][1][1];

		Dir_D[i][0][0] =  (term[iplus1][1][0] - term[i][0][0]);
		Dir_D[i][0][1] =  (term[iplus1][1][1] - term[i][0][1]);
		L_D[i][0] = sqrt(pow(Dir_D[i][0][0],2.0) + pow(Dir_D[i][0][1],2.0));
		Dir_D[i][0][0] /= L_D[i][0];
		Dir_D[i][0][1] /= L_D[i][0];
		S_D[i][0] = (V_term[iplus1][1][0] - V_term[i][0][0])*Dir_D[i][0][0] + (V_term[iplus1][1][1] - V_term[i][0][1])*Dir_D[i][0][1];

		Dir_D[i][1][0] =  (term[iplus1][0][0] - term[i][1][0]);
		Dir_D[i][1][1] =  (term[iplus1][0][1] - term[i][1][1]);
		L_D[i][1] = sqrt(pow(Dir_D[i][1][0],2.0) + pow(Dir_D[i][1][1],2.0));
		Dir_D[i][1][0] /= L_D[i][1];
		Dir_D[i][1][1] /= L_D[i][1];
		S_D[i][1] = (V_term[iplus1][0][0] - V_term[i][1][0])*Dir_D[i][1][0] + (V_term[iplus1][0][1] - V_term[i][1][1])*Dir_D[i][1][1];  

  		// Calculate force contributions on each D/V point

  		//Dorsal forces due to horizontal elements
  		L0_AE = L0_P[i] - fmax(V_muscle[i][0],0)*(L0_P_minus_L_min[i]);  	
  		
  		F_AE = k_AE*fmax(V_muscle[i][0],0)*(L0_AE - L[i][0]);
  		F_PE = k_PE*((L0_P[i] - L[i][0]) + ((L[i][0]-L0_P[i]) > RCONST(0.0))*pow(RCONST(2.0)*(L[i][0]-L0_P[i]),4));
  		F_PD = (D_PE + fmax(V_muscle[i][0],0)*D_AE)*S[i][0];

  		F_H[i][0] = F_PE + F_AE - F_PD;
	  
  		//Ventral forces due to horizontal elements
  		L0_AE = L0_P[i] - fmax(V_muscle[i][1],0)*(L0_P_minus_L_min[i]);  	
  		
  		F_AE = k_AE*fmax(V_muscle[i][1],0)*(L0_AE - L[i][1]);
  		F_PE = k_PE*((L0_P[i] - L[i][1]) + ((L[i][1]-L0_P[i]) > RCONST(0.0))*pow(RCONST(2.0)*(L[i][1]-L0_P[i]),4));
  		F_PD = (D_PE + fmax(V_muscle[i][1],0)*D_AE)*S[i][1];

  		F_H[i][1] = F_PE + F_AE - F_PD;
	
  		//Diagonal forces due to diagonal elements
  		F_D[i][0] = (L0_D[i] - L_D[i][0])*k_DE - D_DE*S_D[i][0];
  		F_D[i][1] = (L0_D[i] - L_D[i][1])*k_DE - D_DE*S_D[i][1];
  	}

  	// If using objects, check for object collisions and calculate associated forces
	if(N_objects > 0){
  		realtype P_x,P_y,Distance,magF,D_scale,magF_P1,magF_P2;
  		ContactForce = 0;
  		for(int i = 0; i < NBAR; ++i){
			for(int j = 0; j < 2; ++j){
				// First ensure they contain zeros
				F_object[i][j][0] = 0;
				F_object[i][j][1] = 0;
				P_x = term[i][j][0];
				P_y = term[i][j][1];

				// Now check proximity to each object
				for(int k = 0; k < N_objects; ++k){
					if((P_x<(Objects[k][0]+Objects[k][2]))&&(P_x>(Objects[k][0]-Objects[k][2]))&&(P_y<(Objects[k][1]+Objects[k][2]))&&(P_y>(Objects[k][1]-Objects[k][2]))){

						//This means the point is within the bounding box of the object, so now we must compute the force (if any)
						dx = P_x - Objects[k][0];
						dy = P_y - Objects[k][1];
						Distance = sqrt(pow(dx,2) + pow(dy,2));
						D_scale = 0.01*Objects[k][2];

						if(Distance < Objects[k][2]){
							magF = k_Object*(Objects[k][2] - Distance) + D_scale*k_Object*(pow((Objects[k][2] - Distance)/D_scale,2));
							F_object[i][j][0] += (dx/Distance)*magF;
							F_object[i][j][1] += (dy/Distance)*magF;
							ContactForce += magF;
						}
					}			
				}
			}
  		}
	}

  	// Add up force contributions for each D/V point
  	F_term[0][0][0] = -F_H[0][0]*Dir[0][0][0] - F_D[0][0]*Dir_D[0][0][0] + F_object[0][0][0];
  	F_term[0][0][1] = -F_H[0][0]*Dir[0][0][1] - F_D[0][0]*Dir_D[0][0][1] + F_object[0][0][1];

  	F_term[0][1][0] = -F_H[0][1]*Dir[0][1][0] - F_D[0][1]*Dir_D[0][1][0] + F_object[0][1][0];
  	F_term[0][1][1] = -F_H[0][1]*Dir[0][1][1] - F_D[0][1]*Dir_D[0][1][1] + F_object[0][1][1];

  	for(int i = 1; i < NSEG; ++i){
		int i_minus_1 = i-1;

		F_term[i][0][0] = F_H[i_minus_1][0]*Dir[i_minus_1][0][0] - F_H[i][0]*Dir[i][0][0] + F_D[i_minus_1][1]*Dir_D[i_minus_1][1][0] - F_D[i][0]*Dir_D[i][0][0] + F_object[i][0][0];
		F_term[i][0][1] = F_H[i_minus_1][0]*Dir[i_minus_1][0][1] - F_H[i][0]*Dir[i][0][1] + F_D[i_minus_1][1]*Dir_D[i_minus_1][1][1] - F_D[i][0]*Dir_D[i][0][1] + F_object[i][0][1];

		F_term[i][1][0] = F_H[i_minus_1][1]*Dir[i_minus_1][1][0] - F_H[i][1]*Dir[i][1][0] + F_D[i_minus_1][0]*Dir_D[i_minus_1][0][0] - F_D[i][1]*Dir_D[i][1][0] + F_object[i][1][0];
		F_term[i][1][1] = F_H[i_minus_1][1]*Dir[i_minus_1][1][1] - F_H[i][1]*Dir[i][1][1] + F_D[i_minus_1][0]*Dir_D[i_minus_1][0][1] - F_D[i][1]*Dir_D[i][1][1] + F_object[i][1][1];
  	}

  	F_term[NSEG][0][0] = F_H[NSEG_MINUS_1][0]*Dir[NSEG_MINUS_1][0][0] + F_D[NSEG_MINUS_1][1]*Dir_D[NSEG_MINUS_1][1][0] + F_object[NSEG][0][0];
  	F_term[NSEG][0][1] = F_H[NSEG_MINUS_1][0]*Dir[NSEG_MINUS_1][0][1] + F_D[NSEG_MINUS_1][1]*Dir_D[NSEG_MINUS_1][1][1] + F_object[NSEG][0][1];

  	F_term[NSEG][1][0] = F_H[NSEG_MINUS_1][1]*Dir[NSEG_MINUS_1][1][0] + F_D[NSEG_MINUS_1][0]*Dir_D[NSEG_MINUS_1][0][0] + F_object[NSEG][1][0];
  	F_term[NSEG][1][1] = F_H[NSEG_MINUS_1][1]*Dir[NSEG_MINUS_1][1][1] + F_D[NSEG_MINUS_1][0]*Dir_D[NSEG_MINUS_1][0][1] + F_object[NSEG][1][1];
  
  	// Convert net forces on D/V points to force and torque	acting on rod CoM
  	for(int i = 0; i < NBAR; ++i){
		realtype cos_thi = cos(CoM[i][2]);
		realtype sin_thi = sin(CoM[i][2]);
		for(int j = 0; j < 2; ++j){			
			F_term_rotated[i][j][0] = F_term[i][j][0]*cos_thi + F_term[i][j][1]*sin_thi;	// This is Fperp
			F_term_rotated[i][j][1] = F_term[i][j][0]*sin_thi - F_term[i][j][1]*cos_thi;    // THis is Fparallel
		}

		V_CoM_rotated[i][0] = (F_term_rotated[i][0][0] + F_term_rotated[i][1][0])/CN[i];

		F_even = (F_term_rotated[i][0][1] + F_term_rotated[i][1][1]);	//Took out the /2
		F_odd = (F_term_rotated[i][1][1] - F_term_rotated[i][0][1])/RCONST(2.0);	

		V_CoM_rotated[i][1] = (F_even)/CL[i];				//Allowing me to take out *2
		V_CoM[i][2] = (F_odd/CL[i])/(M_PI*2.0*R[i]);

		V_CoM[i][0] = V_CoM_rotated[i][0]*cos_thi + V_CoM_rotated[i][1]*sin_thi;
		V_CoM[i][1] = V_CoM_rotated[i][0]*sin_thi - V_CoM_rotated[i][1]*cos_thi;
	
		int three_i = i*3;

		rval[three_i] = V_CoM[i][0] - ypval[three_i];
		rval[three_i+1] = V_CoM[i][1] - ypval[three_i+1];
		rval[three_i+2] = V_CoM[i][2] - ypval[three_i+2];
  	}

  	// Store old lengths for Stretch Receptors 
  	for(int i = 0; i < NSEG; ++i){
		L_SR[i][0] = L[i][0];
		L_SR[i][1] = L[i][1];
  	}

  	return(0);
  }


/*
 *--------------------------------------------------------------------
 * Private functions
 *--------------------------------------------------------------------
 */
 
  // Save output to csv file for visualization
  static void SaveOutput(void *mem, realtype t, N_Vector y){
  
  	float FPS = 25;	// Frame rate at which output should be logged
  	static int tCount = 1.0/(DELTAT*FPS);
  	realtype *yval;
  	int retval, kused;
  	long int nst;
  	realtype hused;
  	
  	double distance; //TOTAL DISTANCE TRAVELLED FOR WORM

  	yval  = NV_DATA_S(y);
  
  	// Save data to file
  	if(tCount == 1.0/(DELTAT*FPS)){
  
  		outfile << t;	
  		for(int i = 0; i < NBAR; ++i){
			outfile << ", " << yval[i*3] << ", " << yval[i*3+1] << ", " << yval[i*3+2];
  		}
  		outfile << "\n";
		tCount = 0;
  	}

  	++tCount;
  	return;  
  }

  double randn(double mu, double sigma) {
	static bool deviateAvailable=false;	//	flag
	static float storedDeviate;			//	deviate from previous calculation
	double polar, rsquared, var1, var2;
	
	//	If no deviate has been stored, the polar Box-Muller transformation is 
	//	performed, producing two independent normally-distributed random
	//	deviates.  One is stored for the next round, and one is returned.
	if (!deviateAvailable) {
		
		//	choose pairs of uniformly distributed deviates, discarding those 
		//	that don't fall within the unit circle
		do {
			var1=2.0*( double(rand())/double(RAND_MAX) ) - 1.0;
			var2=2.0*( double(rand())/double(RAND_MAX) ) - 1.0;
			rsquared=var1*var1+var2*var2;
		} while ( rsquared>=1.0 || rsquared == 0.0);
		
		//	calculate polar tranformation for each deviate
		polar=sqrt(-2.0*log(rsquared)/rsquared);
		
		//	store first deviate and set flag
		storedDeviate=var1*polar;
		deviateAvailable=true;
		
		//	return second deviate
		return var2*polar*sigma + mu;
	}
	
	//	If a deviate is available from a previous call to this function, it is
	//	returned, and the flag is set to false.
	else {
		deviateAvailable=false;
		return storedDeviate*sigma + mu;
	}
  }



  // Print final integrator statistics (Copied from Sundials examples)
  static void PrintFinalStats(void *mem){
  	int retval;
  	long int nst, nni, nje, nre, nreLS, netf, ncfn, nge;

  	retval = IDAGetNumSteps(mem, &nst);
  	check_flag(&retval, "IDAGetNumSteps", 1);
  	retval = IDAGetNumResEvals(mem, &nre);
  	check_flag(&retval, "IDAGetNumResEvals", 1);
  	retval = IDADenseGetNumJacEvals(mem, &nje);
  	check_flag(&retval, "IDADenseGetNumJacEvals", 1);
  	retval = IDAGetNumNonlinSolvIters(mem, &nni);
  	check_flag(&retval, "IDAGetNumNonlinSolvIters", 1);
  	retval = IDAGetNumErrTestFails(mem, &netf);
  	check_flag(&retval, "IDAGetNumErrTestFails", 1);
  	retval = IDAGetNumNonlinSolvConvFails(mem, &ncfn);
  	check_flag(&retval, "IDAGetNumNonlinSolvConvFails", 1);
  	retval = IDADenseGetNumResEvals(mem, &nreLS);
  	check_flag(&retval, "IDADenseGetNumResEvals", 1);
  	retval = IDAGetNumGEvals(mem, &nge);
  	check_flag(&retval, "IDAGetNumGEvals", 1);

  	printf("\nFinal Run Statistics: \n\n");
  	printf("Number of steps                    = %ld\n", nst);
  	printf("Number of residual evaluations     = %ld\n", nre+nreLS);
  	printf("Number of Jacobian evaluations     = %ld\n", nje);
  	printf("Number of nonlinear iterations     = %ld\n", nni);
  	printf("Number of error test failures      = %ld\n", netf);
  	printf("Number of nonlinear conv. failures = %ld\n", ncfn);
  	printf("Number of root fn. evaluations     = %ld\n", nge);
  }

/*
 * Check function return value... (Copied from Sundials examples)
 *   opt == 0 means SUNDIALS function allocates memory so check if
 *            returned NULL pointer
 *   opt == 1 means SUNDIALS function returns a flag so check if
 *            flag >= 0
 *   opt == 2 means function allocates memory so check if returned
 *            NULL pointer 
 */

static int check_flag(void *flagvalue, char *funcname, int opt)
{
  int *errflag;
  /* Check if SUNDIALS function returned NULL pointer - no memory allocated */
  if (opt == 0 && flagvalue == NULL) {
    fprintf(stderr, 
            "\nSUNDIALS_ERROR: %s() failed - returned NULL pointer\n\n", 
            funcname);
    return(1);
  } else if (opt == 1) {
    /* Check if flag < 0 */
    errflag = (int *) flagvalue;
    if (*errflag < 0) {
      fprintf(stderr, 
              "\nSUNDIALS_ERROR: %s() failed with flag = %d\n\n", 
              funcname, *errflag);
      return(1); 
    }
  } else if (opt == 2 && flagvalue == NULL) {
    /* Check if function returned NULL pointer - no memory allocated */
    fprintf(stderr, 
            "\nMEMORY_ERROR: %s() failed - returned NULL pointer\n\n", 
            funcname);
    return(1);
  }

  return(0);
}

/*------Constants for RandomUniform()---------------------------------------
#define SEED 3
#define IM1 2147483563
#define IM2 2147483399
#define AM (1.0/IM1)
#define IMM1 (IM1-1)
#define IA1 40014
#define IA2 40692
#define IQ1 53668
#define IQ2 52774
#define IR1 12211
#define IR2 3791
#define NTAB 32
#define NDIV (1+IMM1/NTAB)
#define EPS 1.2e-7
#define RNMX (1.0-EPS)

double rnd_num(double minValue,double maxValue)
{
	long j;
	long k;
	static long idum;
	static long idum2=123456789;
	static long iy=0;
	static long iv[NTAB];
	double result;

	if (iy == 0)
		idum = SEED;

	if (idum <= 0)
	{
		if (-idum < 1)
			idum = 1;
		else
			idum = -idum;

		idum2 = idum;

		for (j=NTAB+7; j>=0; j--)
		{
			k = idum / IQ1;
			idum = IA1 * (idum - k*IQ1) - k*IR1;
			if (idum < 0) idum += IM1;
			if (j < NTAB) iv[j] = idum;
		}

		iy = iv[0];
	}

	k = idum / IQ1;
	idum = IA1 * (idum - k*IQ1) - k*IR1;

	if (idum < 0)
		idum += IM1;

	k = idum2 / IQ2;
	idum2 = IA2 * (idum2 - k*IQ2) - k*IR2;

	if (idum2 < 0)
		idum2 += IM2;

	j = iy / NDIV;
	iy = iv[j] - idum2;
	iv[j] = idum;

	if (iy < 1)
		iy += IMM1;

	result = AM * iy;

	if (result > RNMX)
		result = RNMX;

	result = minValue + result * (maxValue - minValue);
	return(result);
}*/
