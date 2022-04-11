document.getElementById('date').innerHTML = "Date: " + new Date().toDateString();
var a=[['maggi','hd63g',2,2,4],['chocolate','dhg232d',1,2,2]];
var totalcost=0;


for(var i=0;i<2;i++)
    {
        var mg=document.createElement("IMG");
        mg.setAttribute("width","25");
        mg.setAttribute("height",25);
        
        var table=document.getElementById('bill');
        var row=table.insertRow(-1);
        var cell1=row.insertCell(0);
        var cimg=a[i][0]+".jpg";
        mg.setAttribute("src",cimg.toString());
        cell1.appendChild(mg);
        
        for(var j=1;j<6;j++)
            {
             var cell=row.insertCell();
            cell.innerHTML=a[i][j-1];
            }
    
        totalcost+=a[i][4];
        
    }
document.getElementById('cost').innerHTML="Total cost= "+totalcost;