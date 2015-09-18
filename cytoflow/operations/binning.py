'''
Created on Sep 18, 2015

@author: brian
'''

from __future__ import division

from traits.api import HasStrictTraits, Str, CStr, List, Float, Int, Enum
import numpy as np
import matplotlib as mpl
from traits.has_traits import provides
from cytoflow.operations.i_operation import IOperation

@provides(IOperation)
class BinningOp(HasStrictTraits):
    """
    Bin data along an axis.
    
    This operation creates equally spaced bins (in linear or log space)
    along an axis and adds a metadata column assigning each event to a bin.
    
    Attributes
    ----------
    name : Str
        The operation name.  Used to name the new metadata field in the
        experiment that's created by apply()
        
    channel : Str
        The name of the channel along which to bin.
        
    num_bins = Int
        The number of bins to make
        
    scale : Enum("Linear", "Log")
        Make the bins equidistant along what scale?
        TODO - add other scales, like Logicle        
    """
    
    # traits
    id = "edu.mit.synbio.cytoflow.operations.binning"
    friendly_id = "Binning"
    
    name = CStr()
    channel = Str()
    num_bins = Int()
    scale = Enum("linear", "log10")
    
    def is_valid(self, experiment):
        """Validate this operation against an experiment."""

        if not self.name:
            return False
        
        if self.name in experiment.data.columns:
            return False
        
        if not self.channel:
            return False
        
        if not self.channel in experiment.channels:
            return False
              
        if not self.num_bins or self.num_bins <= 0:
            return False
       
        return True
    
    
    def apply(self, old_experiment):
        """Applies the binning to an experiment.
        
        Parameters
        ----------
        experiment : Experiment
            the old_experiment to which this op is applied
            
        Returns
        -------
            a new experiment, the same as old_experiment but with a new
            column the same as the operation name.  The bool is True if the
            event's measurement in self.channel is greater than self.low and
            less than self.high; it is False otherwise.
        """
        
        # make sure name got set!
        if not self.name:
            raise RuntimeError("You have to set the Binning operations's name "
                               "before applying it!")
        
        # make sure old_experiment doesn't already have a column named self.name
        if(self.name in old_experiment.data.columns):
            raise RuntimeError("Experiment already contains a column {0}"
                               .format(self.name))    
            
        channel_min = old_experiment.data[self.channel].min()
        channel_max = old_experiment.data[self.channel].max()
        if self.scale == "linear":
            bins = np.linspace(start = channel_min, stop = channel_max,
                               num = self.num_bins)
        elif self.scale == "log10":
            bins = np.logspace(start = np.log10(channel_min),
                               stop = np.log10(channel_max),
                               num = self.num_bins,
                               base = 10) 
            
        # bins need to be internal; drop the first and last one
        bins = bins[1:-1]
            
        new_experiment = old_experiment.clone()
        new_experiment[self.name] = np.digitize(old_experiment[self.channel], bins)
        
        new_experiment.conditions[self.name] = "int"
        new_experiment.metadata[self.name] = {}
        
        return new_experiment
        