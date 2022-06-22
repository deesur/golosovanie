pragma solidity ^0.8.7;

contract Admin {
    address admin = msg.sender;

    function administrate() public view returns(address) {
        return admin;
    }

    modifier onlyadmin { 
        require(msg.sender == admin, "You are not administrator!");
        _;
    }
}

contract Vibor is Admin{
    modifier onlycommis(uint _index) {
        require(mem[_index][msg.sender], "You are not a commiss member!");
        _;
    }
    struct Voting {
    	string name;
    	string date;
    }
    
    struct Candidate {
        string fName;
        uint score;
    }

    Voting[] votings; // список голосований

    mapping(uint=>Candidate[]) candidates; // список решений в голосовании
    mapping(uint=>mapping(address=>bool)) izb; // список избирателей
    mapping(address=>string) izb_fio; // список имен избирателей
    mapping(uint=>mapping(address=>uint)) result;

    mapping(uint=>mapping(address=>bool)) mem;

    function addVote (string memory _date, string memory _name) onlyadmin public returns(uint){
        Voting memory v;
        v.name = _name;
        v.date = _date;
        votings.push(v);
        return votings.length;
    }

    function addMember (address _addr, uint _index) onlyadmin public {
        if (_index < votings.length) {
            mem[_index][_addr] = true;
        }   
        else revert("Index is out of range!");
    }

    function addCandidate (string memory _name, uint _index) onlycommis(_index) public {
        Candidate memory c;
        c.fName = _name;
        c.score = 0;
        if (_index < votings.length) 
            candidates[_index].push(c);
        else revert("Index is out of range!");
    }

    function addIzbir (address _addr, uint _index, string memory _name) onlycommis(_index) public {
        if (_index < votings.length) {
            izb[_index][_addr] = true;
            izb_fio[_addr] = _name;           
        }   
        else revert("Index is out of range!");
    }

    function checkIzb (address _addr, uint _index) public view returns (bool) {
        return izb[_index][_addr];
    }

    function checkMem (address _addr, uint _index) public view returns (bool) {
        return mem[_index][_addr];
    }

    function getCandidates (uint index) view public returns (string[] memory names, uint[] memory ind) {
        names = new string[](candidates[index].length);
        ind = new uint[](candidates[index].length);
        for(uint i=0;i<candidates[index].length;i++) {
            names[i] = candidates[index][i].fName;
            ind[i] = i;
        } 
        return (names,ind);
    }

    function getResults (uint index) view public returns (Candidate[] memory){
        return candidates[index];
    }   

    function golosovanie (uint _index, address _addr, uint choice) public {
        if (_index < votings.length){
            if (izb[_index][_addr] == true) {
                if (choice < candidates[_index].length){
                    candidates[_index][choice].score+=1;
                    izb[_index][_addr] = false;
                }
            }
            else revert("You are not on list or had already voted!");
        } 
        else revert("Index is out of range!");
    }

    function getVotings(uint index) public view returns(string memory) {
        return votings[index].name;
    }
}